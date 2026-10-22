from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Grant Finder")


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """
    <html>
      <head><title>Grant Finder</title></head>
      <body>
        <h1>Grant Finder</h1>
        <form>
          <label for="org-profile">Organization profile</label>
          <textarea id="org-profile" name="org-profile" rows="6" cols="60"></textarea>
          <br><br>
          <button type="submit">Find grants</button>
        </form>
      </body>
    </html>
    """


@app.get("/api/grants")
def grant_matches() -> dict[str, object]:
    return {
        "org_type": "501(c)(3)",
        "island": "O'ahu",
        "focus": ["youth education", "STEM", "Hawaiian culture"],
        "budget": 350000,
        "needs": ["equipment", "summer programming"],
        "matches": [],
    }
