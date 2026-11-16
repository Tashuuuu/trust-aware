from streamlit.testing.v1 import AppTest

at = AppTest.from_file("../app/streamlit_app.py", default_timeout=240).run()
for e in at.exception:
    print("EXCEPTION:", e.value)
    print(e.stack_trace)
print("subheaders:", len(at.subheader), "| errors:", len(at.error), "| warnings:", len(at.warning))