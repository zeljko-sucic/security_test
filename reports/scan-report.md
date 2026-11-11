# HelpSpace — scanner findings

Actual Semgrep 1.152.0 scan using local educational rules. 7 findings across 4 scanned Python files. Scanner priority is an initial triage label, not a verified impact assessment. Some alerts may not be exploitable; other issues may be absent from this report.

See `manifest.json` for the exact command and source hashes.

## HS-01 — scan-rules.legacy-digest-review

**Scanner priority:** Medium · **Location:** `helpdesk/__init__.py:43`

MD5 is used. Determine whether this digest protects secrets, authenticity, integrity, or only non-security metadata.

```text
  41      # Cache-busting identifier for the stylesheet; not a session or integrity token.
  42      stylesheet = Path(app.static_folder) / "style.css"
  43      asset_version = hashlib.md5(stylesheet.read_bytes(), usedforsecurity=False).hexdigest()[:12]
  44      app.jinja_env.globals["asset_version"] = asset_version
  45      return app
```

## HS-02 — scan-rules.debug-server-configuration

**Scanner priority:** Critical · **Location:** `helpdesk/__main__.py:9`

The application server accepts a runtime debug setting. Determine its effective value and exposure in the supplied deployment.

```text
   7  if __name__ == "__main__":
   8      debug_enabled = os.environ.get("HELPSPACE_DEBUG", "0") == "1"
   9      app.run(
  10          host=os.environ.get("HELPSPACE_HOST", "127.0.0.1"),
  11          port=8080,
  12          debug=debug_enabled,
  13          use_reloader=False,
  14      )
```

## HS-03 — scan-rules.login-query-review

**Scanner priority:** High · **Location:** `helpdesk/routes.py:54`

User lookup receives an email used by a database query. Verify whether SQL structure can be influenced by that value.

```text
  52
  53  def find_user(email):
  54      return get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
  55
  56
```

## HS-04 — scan-rules.html-trust-boundary

**Scanner priority:** Medium · **Location:** `helpdesk/routes.py:59`

Markup creates trusted HTML. Check the origin of the value, interpolation behavior, and the rendering context.

```text
  57  @bp.app_template_filter("badge")
  58  def badge(label):
  59      return Markup('<span class="badge">{}</span>').format(label)
  60
  61
```

## HS-05 — scan-rules.html-trust-boundary

**Scanner priority:** Medium · **Location:** `helpdesk/routes.py:64`

Markup creates trusted HTML. Check the origin of the value, interpolation behavior, and the rendering context.

```text
  62  @bp.app_template_filter("comment_html")
  63  def comment_html(body):
  64      return Markup(body)
  65
  66
```

## HS-06 — scan-rules.sql-execution-review

**Scanner priority:** High · **Location:** `helpdesk/routes.py:99`

SQL is executed without bound parameters at this call. Trace how the statement is constructed and whether request data can change its structure.

```text
  97      term = request.args.get("q", "")
  98      query = f"SELECT * FROM tickets WHERE organization_id = {g.user['organization_id']} AND title LIKE '%{term}%' ORDER BY id"
  99      rows = get_db().execute(query).fetchall()
 100      return render_template("tickets.html", tickets=rows, query=term)
 101
```

## HS-07 — scan-rules.profile-role-input

**Scanner priority:** Medium · **Location:** `helpdesk/routes.py:143`

A role value is accepted from a form. Check who can submit it and whether the server authorizes the resulting role change.

```text
 141      if request.method == "POST":
 142          name = request.form.get("display_name", "").strip()
 143          role = request.form.get("role", g.user["role"])
 144          if not name or len(name) > 80 or role not in ("member", "admin"):
 145              abort(400, "Invalid profile")
```
