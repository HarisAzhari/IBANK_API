from flask import Flask, request, jsonify
from flask_cors import CORS
import time
from datetime import datetime
from ibank import IBANScraper

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Initialize the IBAN scraper
scraper = IBANScraper()


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify API is running"""
    return (
        jsonify(
            {
                "status": "healthy",
                "message": "IBAN API is running smoothly! 💫",
                "timestamp": datetime.now().isoformat(),
                "service": "IBAN Swift Code Lookup API",
            }
        ),
        200,
    )


@app.route("/get-swift-code", methods=["POST"])
def get_swift_code():
    """
    Get Swift/BIC code for a given IBAN

    Expected payload:
    {
        "iban": "RO49AAAA1B31007593840000"
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()

        # Validate input
        if not data:
            return (
                jsonify(
                    {
                        "error": "No data provided",
                        "message": "Please provide JSON data with 'iban' field",
                    }
                ),
                400,
            )

        iban = data.get("iban")

        if not iban:
            return (
                jsonify(
                    {
                        "error": "Missing IBAN",
                        "message": "Please provide 'iban' field in the request body",
                    }
                ),
                400,
            )

        # Clean up IBAN (remove spaces, convert to uppercase)
        iban = iban.replace(" ", "").upper().strip()

        if not iban:
            return (
                jsonify({"error": "Invalid IBAN", "message": "IBAN cannot be empty"}),
                400,
            )

        # Scrape IBAN information
        print(f"🔍 Processing IBAN: {iban}")
        iban_data = scraper.scrape_iban_info(iban)

        if iban_data:
            # Success response
            response_data = {
                "success": True,
                "iban": iban,
                "swift_bic_code": iban_data.get("swift_bic_code", "N/A"),
                "bank_name": iban_data.get("bank_name", "N/A"),
                "country": iban_data.get("country", "N/A"),
                "city": iban_data.get("city", "N/A"),
                "scraped_at": iban_data.get("scraped_at", datetime.now().isoformat()),
                "processing_time": f"Processed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            }

            print(f"✅ Successfully scraped data for {iban}")
            return jsonify(response_data), 200

        else:
            # Failed to scrape
            error_response = {
                "success": False,
                "error": "Scraping failed",
                "message": f"Unable to retrieve Swift code information for IBAN: {iban}",
                "iban": iban,
                "failed_at": datetime.now().isoformat(),
            }

            print(f"❌ Failed to scrape data for {iban}")
            return jsonify(error_response), 404

    except Exception as e:
        # Handle unexpected errors
        error_response = {
            "success": False,
            "error": "Internal server error",
            "message": str(e),
            "timestamp": datetime.now().isoformat(),
        }

        print(f"💥 Error processing request: {e}")
        return jsonify(error_response), 500


@app.route("/", methods=["GET"])
def root():
    """Root endpoint with API information"""
    return (
        jsonify(
            {
                "message": "Welcome to the IBAN Swift Code API! 😍",
                "version": "1.0.0",
                "endpoints": {
                    "health": "/health - Check API health status",
                    "get_swift_code": "/get-swift-code - Get Swift/BIC code for an IBAN (POST)",
                },
                "usage": {
                    "method": "POST",
                    "url": "/get-swift-code",
                    "payload": {"iban": "RO49AAAA1B31007593840000"},
                },
                "timestamp": datetime.now().isoformat(),
            }
        ),
        200,
    )


if __name__ == "__main__":
    print("🔥 Starting IBAN Swift Code API...")
    print("💫 API will be available at http://localhost:5000")
    print("🚀 Use /get-swift-code endpoint to lookup Swift codes!")

    app.run(debug=True, host="0.0.0.0", port=5000)
