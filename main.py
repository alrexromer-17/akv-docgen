from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from fpdf import FPDF
import uuid
import os

app = FastAPI()

env = Environment(loader=FileSystemLoader("templates"))
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def form(request: Request):
    return HTMLResponse(content="""
        <h2>Generate Legal Document</h2>
        <form method="post" id="docForm">
            <label>Document Type:</label><br>
            <select name="doc_type" id="doc_type" onchange="showFields()">
                <option value="rent_agreement">Rent Agreement</option>
                <option value="affidavit">Affidavit</option>
                <option value="death_certificate">Death Certificate</option>
            </select><br><br>

            <div id="fields"></div>

            <button type="submit">Generate Document</button>
        </form>

        <script>
            function showFields() {
                const docType = document.getElementById("doc_type").value;
                const fieldsDiv = document.getElementById("fields");
                let html = "";

                if (docType === "rent_agreement") {
                    html = `
                        Landlord Name: <input name="landlord_name"><br><br>
                        Landlord Address: <input name="landlord_address"><br><br>
                        Tenant Name: <input name="tenant_name"><br><br>
                        Tenant Address: <input name="tenant_address"><br><br>
                        Property Address: <input name="property_address"><br><br>
                        Monthly Rent: <input name="monthly_rent"><br><br>
                        Security Deposit: <input name="security_deposit"><br><br>
                        Start Date: <input type="date" name="start_date"><br><br>
                        End Date: <input type="date" name="end_date"><br><br>
                        Agreement Date: <input type="date" name="date"><br><br>
                    `;
                } else if (docType === "affidavit") {
                    html = `
                        Affiant Name: <input name="affiant_name"><br><br>
                        Parent Name: <input name="parent_name"><br><br>
                        Age: <input name="age"><br><br>
                        Address: <input name="address"><br><br>
                        Statement: <textarea name="statement"></textarea><br><br>
                        Place: <input name="place"><br><br>
                        Date: <input type="date" name="date"><br><br>
                    `;
                } else if (docType === "death_certificate") {
                    html = `
                        Applicant Name: <input name="applicant_name"><br><br>
                        Applicant Address: <input name="applicant_address"><br><br>
                        Deceased Name: <input name="deceased_name"><br><br>
                        Date of Death: <input type="date" name="date_of_death"><br><br>
                        Place of Death: <input name="place_of_death"><br><br>
                        Relation: <input name="relation"><br><br>
                        Municipal Office: <input name="municipal_office"><br><br>
                        Date: <input type="date" name="date"><br><br>
                    `;
                }

                fieldsDiv.innerHTML = html;
            }

            window.onload = showFields;
        </script>
    """)


@app.post("/", response_class=HTMLResponse)
async def generate_doc(
    request: Request,
    doc_type: str = Form(...)
):
    form = await request.form()
    data = dict(form)
    data.pop("doc_type")  # remove this key from template context

    try:
        # Render template
        template = env.get_template(f"{doc_type}.txt")
        rendered = template.render(data)

        # Create PDF
        pdf = FPDF()
        pdf.add_page()

        # Font path
        font_path = os.path.join("static", "DejaVuSans.ttf")
        if not os.path.exists(font_path):
            return HTMLResponse(
                content=f"<h3>❌ Font file missing at: {font_path}</h3>",
                status_code=500,
            )

        pdf.set_font("Arial", size=12)

        for line in rendered.split("\n"):
            pdf.multi_cell(0, 10, txt=line.strip())

        filename = f"{doc_type}_{uuid.uuid4().hex[:6]}.pdf"
        output_path = os.path.join("static", filename)
        pdf.output(output_path)

        return HTMLResponse(content=f"""
            <h3>✅ PDF Document Generated</h3>
            <a href="/static/{filename}" target="_blank">📄 Download {filename}</a><br><br>
            <a href="/">🔁 Generate Another</a>
        """)
    
    except Exception as e:
        return HTMLResponse(
            content=f"<h3>❌ Error during PDF generation</h3><pre>{str(e)}</pre>",
            status_code=500,
        )