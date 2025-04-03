from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEST_TO_TABLE_MAP = {
    "CBC": {"table": "medical_request_form_hermatology", "field": "cbc"},
    "Glucose": {"table": "medical_request_form_diabetes", "field": "Glucose"},
    "HbA1C": {"table": "medical_request_form_diabetes", "field": "HbA1C"},
    "Creatinine": {"table": "medical_request_form_kidney", "field": "Creatinine"},
    "Uric Acid": {"table": "medical_request_form_kidney", "field": "Uric_Acid"},
    "Sodium": {"table": "medical_request_form_electrolytes", "field": "Sodium"},
    "Potassium": {"table": "medical_request_form_electrolytes", "field": "Potassium"},
    "ALT": {"table": "medical_request_form_liver", "field": "ALT"},
    "Cholesterol": {"table": "medical_request_form_lipid", "field": "Cholesterol"},
    "Rubella": {"table": "medical_request_form_immunology", "field": "rubella"},
    "Pregnancy Test": {"table": "medical_request_form_immunology", "field": "pregnancyTestUrine"},
    "Mononucleosis": {"table": "medical_request_form_immunology", "field": "mononucleosis"},
    "Prenatal Antibody": {"table": "medical_request_form_immunology", "field": "prenatalABORhDAntibody"},
    "Repeat Prenatal": {"table": "medical_request_form_immunology", "field": "repeatPrenatalAntibodies"},
    "Cervical Swab": {"table": "medical_request_form_microbiology_id_sensitivities", "field": "cervicalSwab"},
    "Vaginal Swab": {"table": "medical_request_form_microbiology_id_sensitivities", "field": "vaginalSwab"},
    "Group B Strep": {"table": "medical_request_form_microbiology_id_sensitivities", "field": "vaginalRectalGroupBStrep"},
    "Chlamydia": {"table": "medical_request_form_microbiology_id_sensitivities", "field": "chlamydia"},
    "Chlamydia Source": {"table": "medical_request_form_microbiology_id_sensitivities", "field": "chlamydiaSource"},
    "GC": {"table": "medical_request_form_microbiology_id_sensitivities", "field": "gc"},
    "Sputum": {"table": "medical_request_form_microbiology_id_sensitivities", "field": "sputum"},
    "Throat Swab": {"table": "medical_request_form_microbiology_id_sensitivities", "field": "throatSwab"},
    "Wound Swab": {"table": "medical_request_form_microbiology_id_sensitivities", "field": "woundSwab"},
    "Urine Culture": {"table": "medical_request_form_microbiology_id_sensitivities", "field": "urineCulture"},
    "Stool Culture": {"table": "medical_request_form_microbiology_id_sensitivities", "field": "stoolCulture"},
    "Acute Hepatitis": {"table": "medical_request_form_hepatitis", "field": "acuteHepatitis"},
    "Chronic Hepatitis": {"table": "medical_request_form_hepatitis", "field": "chronicHepatitis"},
    "Immune Status": {"table": "medical_request_form_hepatitis", "field": "immuneStatusExposure"},
    "Hepatitis A": {"table": "medical_request_form_hepatitis", "field": "hepatitisA"},
    "Hepatitis B": {"table": "medical_request_form_hepatitis", "field": "hepatitisB"},
    "Hepatitis C": {"table": "medical_request_form_hepatitis", "field": "hepatitisC"},
    "Total PSA": {"table": "medical_request_form_psa", "field": "totalPSA"},
    "Free PSA": {"table": "medical_request_form_psa", "field": "freePSA"},
    "Insured PSA": {"table": "medical_request_form_psa", "field": "insuredPSA"},
    "Uninsured PSA": {"table": "medical_request_form_psa", "field": "uninsuredPSA"},
    "Insured Vitamin D": {"table": "medical_request_form_vitamind", "field": "insuredVitaminD"},
    "Uninsured Vitamin D": {"table": "medical_request_form_vitamind", "field": "uninsuredVitaminD"},
}

class TestRequest(BaseModel):
    text: str
    speech: bool

class ConfirmRequest(BaseModel):
    tests: list[str]
    medical_request_form_id: int

@app.get("/")
async def root():
    return {"message": "Voice Medical Chatbot API is running"}

@app.post("/process")
async def process_text(request: TestRequest):
    text = request.text.strip().lower()
    detected_tests = [test for test in TEST_TO_TABLE_MAP if test.lower() in text]

    if not detected_tests:
        return {"reply": "No tests recognized.", "confirmedTest": []}

    return {"reply": f"Detected tests: {', '.join(detected_tests)}", "confirmedTest": detected_tests}


@app.post("/finalize")
def finalize(payload: dict):
    try:
        tests = payload.get("tests", [])
        form_id = payload.get("medical_request_form_id")
        print(f"📦 Finalizing for form ID: {form_id} with tests: {tests}")

        table_test_map = {
            "medical_request_form_hermatology": ["cbc", "prothrombinTime"],
            "medical_request_form_immunology": ["pregnancyTestUrine", "mononucleosis", "rubella", "prenatalABORhDAntibody", "repeatPrenatalAntibodies"],
            "medical_request_form_microbiology_id_sensitivities": ["cervicalSwab", "vaginalSwab", "vaginalRectalGroupBStrep", "chlamydia", "chlamydiaSource", "gc", "sputum", "throatSwab", "woundSwab", "urineCulture", "stoolCulture"],
            "medical_request_form_hepatitis": ["acuteHepatitis", "chronicHepatitis", "immuneStatusExposure", "hepatitisA", "hepatitisB", "hepatitisC"],
            "medical_request_form_psa": ["totalPSA", "freePSA", "insuredPSA", "uninsuredPSA"],
            "medical_request_form_vitamind": ["insuredVitaminD", "uninsuredVitaminD"]
        }

        for table_name, test_fields in table_test_map.items():
            matched_fields = [t for t in tests if t in test_fields]
            if not matched_fields:
                continue

            try:
                get_url = f"https://e-react-node-backend-22ed6864d5f3.herokuapp.com/table/{table_name}"
                response = requests.get(get_url)
                response.raise_for_status()
                rows = response.json()
                existing_row = next((row for row in rows if row.get("medical_request_form_id") == form_id), None)

                if existing_row:
                    row_id = existing_row["id"]
                    delete_url = f"{get_url}/{row_id}"
                    print(f"🗑️ Deleting existing row: {delete_url}")
                    requests.delete(delete_url)
                else:
                    print(f"ℹ️ No existing row in {table_name} for form ID {form_id}")

                new_row = {"medical_request_form_id": form_id}
                for field in matched_fields:
                    new_row[field] = 1

                print(f"➕ Re-inserting row: {new_row}")
                requests.post(get_url, json=new_row)

            except Exception as e:
                print(f"❌ Error processing table '{table_name}':", str(e))

        return {"detail": "Tests updated successfully."}

    except Exception as e:
        print("❌ Failed to update tests:", str(e))
        return {"detail": f"Failed to update tests: {str(e)}"}, 500
    if not request.tests:
        raise HTTPException(status_code=400, detail="No tests provided.")
    if not request.medical_request_form_id:
        raise HTTPException(status_code=400, detail="Missing medical_request_form_id.")

    try:
        base_url = "https://e-react-node-backend-22ed6864d5f3.herokuapp.com/table/"
        responses = []

        for test in request.tests:
            if test not in TEST_TO_TABLE_MAP:
                continue

            table_info = TEST_TO_TABLE_MAP[test]
            table = table_info["table"]
            field = table_info["field"]
            full_url = base_url + table

            # Step 1: Get existing data
            existing_data = requests.get(full_url).json()
            matched_row = next((row for row in existing_data if row.get("medical_request_form_id") == request.medical_request_form_id), None)

            if matched_row:
                delete_id = matched_row["id"]
                delete_url = f"{full_url}/{delete_id}"
                print(f"🗑️ Deleting existing row: {delete_url}")
                requests.delete(delete_url)

            # Step 2: Build new row
            new_row = {"medical_request_form_id": request.medical_request_form_id}
            for test_name in request.tests:
                info = TEST_TO_TABLE_MAP[test_name]
                new_row[info["field"]] = 1

            print(f"➕ Re-inserting row: {new_row}")
            res = requests.post(full_url, json=new_row)
            responses.append({test: res.status_code})

        return {"message": "Tests updated via delete+post", "results": responses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update tests: {e}")