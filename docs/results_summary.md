# Results summary (auto-generated)

```

## 1 files exist
missing: none

## 2 corpus
raw rows 17880 -> final 15560 (removed 2320)
       count  sum    mean
split                    
test    3112  131  0.0421
train  12448  524  0.0421
shared company profiles train/test: 0 | duplicate search_text: 0
postings with >=1 skill: 0.743

## 3 BM25 baseline = norm
BASELINE in code: norm | runs/bm25.json equals norm run: True

## 4 BM25 top-5 (norm)
q1: entry-level data analyst internship requiring Python and SQL
    17.69 | Data Analyst
    16.90 | Data Analyst (internship)
    16.57 | Data Analyst Intern
    15.84 | French speaking data analyst
    15.06 | Data Analyst
q2: machine learning internship for a fresher with Python and scikit-learn
    24.08 | Senior Data Scientist
    23.77 | Data Scientist
    18.93 | Statistician
    17.96 | Robust speech separation and recognition
    17.88 | Robust speech recognition and understanding
q3: remote internship with no prior work experience required
    16.78 | Marketing Intern
    16.07 | Animation Intern
    15.97 | Research and Development Part-Time Internship
    15.66 | Technical Support Representative
    15.40 | Quality Assurance Intern
q4: work-from-home data entry role promising high earnings with no experience
    15.72 | Data Entry / Administrative Assitstant / Admin Clerk / Office Assistan
    15.45 | Data Entry Clerk
    15.41 | Sales Account Executive
    14.23 | Payroll Data Entry Clerk Position - Earn $100-$200 Daily
    14.21 | SENIOR SOFTWARE ENGINEER
q5: software engineering internship requiring Java and database skills
    15.59 | Field Engineer
    15.51 | Senior Software Developer(Java)
    15.34 | R&D - Software Engineer
    15.27 | Data Science Intern
    15.23 | Intern & Graduate / Open Positions

## 5 rules + severities
severities: {'asks_for_money': 'medium', 'sensitive_documents': 'medium', 'chat_app_contact': 'low', 'unrealistic_earnings': 'medium', 'scam_job_type': 'low', 'no_experience_big_pay': 'low', 'pressure': 'low'}
split=train fraud=524 real=11924
                 rule  fires  on_fraud  on_real  precision  recall  real_fire_rate
       asks_for_money      5         2        3      0.400   0.004           0.000
no_experience_big_pay     61        14       47      0.230   0.027           0.004
        vague_company   2456       357     2099      0.145   0.681           0.176
 unrealistic_earnings     15         2       13      0.133   0.004           0.001
 email_but_no_website    470        50      420      0.106   0.095           0.035
             pressure      5         0        5      0.000   0.000           0.000
     chat_app_contact     29         0       29      0.000   0.000           0.002
  sensitive_documents      5         0        5      0.000   0.000           0.000
        scam_job_type     29         0       29      0.000   0.000           0.002

## 6 classifier
train: n=12448 fraud=524 PR-AUC=0.681 precision=0.397 recall=0.750 F1=0.519 false_alarm_rate=0.050 tn/fp/fn/tp=11327/597/131/393
test: n=3112 fraud=131 PR-AUC=0.657 precision=0.318 recall=0.718 F1=0.440 false_alarm_rate=0.068 tn/fp/fn/tp=2779/202/37/94
threshold: 0.4489

## 7 risk levels on train/test
train:
fraudulent             0    1  fraud_share
level                                     
high                 359  354        0.496
insufficient_info    135   13        0.088
low                11195  126        0.011
medium               235   31        0.117
test:
fraudulent            0   1  fraud_share
level                                   
high                118  88        0.427
insufficient_info    38   1        0.026
low                2742  36        0.013
medium               83   6        0.067
test base rate 0.042; high-level fraud share on test 0.427

## 8 unit tests
..................                                                       [100%]
18 passed in 8.09s

## 9 app smoke test
exceptions: [] | result cards rendered: 5

## 10 repo hygiene
requirements missing: none
tracked files: 6 | >20MB: [] | sensitive: []
git status (first 15):
M README.md
 M requirements.txt
?? app/
?? data/
?? docs/
?? notebooks/
?? pytest.ini
?? reports/
?? risk/eval_rules.py
?? risk/model.joblib
?? risk/probs.parquet
?? risk/risk_report.py
?? risk/risk_reports.json
?? risk/rules.py
?? risk/threshold.json

## SUMMARY
PASS  1 files exist
PASS  2 corpus
PASS  3 BM25 baseline = norm
PASS  4 BM25 top-5 (norm)
PASS  5 rules + severities
PASS  6 classifier
PASS  7 risk levels on train/test
PASS  8 unit tests
PASS  9 app smoke test
PASS  10 repo hygiene
```
