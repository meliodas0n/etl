import pandas as pd, re

df = pd.DataFrame([], columns=['customer_id', 'age', 'email'])

def validate_customers(df):
  errors = []
  if df['customer_id'].duplicated().any():
    errors.append("Duplicate IDs found")
  if (df['age'] < 0).any():
    errors.append("Negativ ages")
  if not df['email'].str.contains('@').all():
    errors.append("Invalid emails")
  return errors

# Traditional approach
if df['age'].min() < 0 or df['age'].max() > 120:
  raise ValueError("Invalid ages found")

# DSL Approach
# validator.add_rule(Rule("Valid ages", between('age', 0, 120), "Ages must be 0-120"))

customers = pd.DataFrame({
  'customer_id': [101, 102, 103, 103, 105],
  'email': ['john@gmail.com', 'invalid-email', '', 'sarah@yahoo.com', 'mike@domain.co'],
  'age': [25, -5, 35, 200, 28],
  'total_spent': [250.50, 1200.00, 0.00, -50.00, 899.99],
  'join_date': ['2023-01-15', '2023-13-45', '2023-02-20', '2023-02-20', '']
}) # Note: 2023-13-45 is an intentionally malformed date.

class Rule:
  def __init__(self, name, condition, error_msg):
    self.name = name
    self.condition = condition
    self.error_msg = error_msg

  def check(self, df):
    # The condition function returns True for VALID rows.
    # We use - (bitwise NOT) to select the rows that VIOLATE the condition.
    violations = df[~self.condition(df)]
    if not violations.empty:
      return {
        'rule': self.name,
        'message': self.error_msg,
        'violations': len(violations),
        'sample_rows': violations.head(3).index.tolist()
      }
    return None

class DataValidator:
  def __init__(self):
    self.rules = []
  
  def add_rule(self, rule):
    self.rules.append(rule)
    return self # Enables method chaining
  
  def validate(self, df):
    results = []
    for rule in self.rules:
      violation = rule.check(df)
      if violation:
        results.append(violation)
    return results

def not_null(column): return lambda df: df[column].notna()
def unique_values(column): return lambda df: ~df.duplicated(subset=[column], keep=False)
def between(column, min_val, max_val): return lambda df: df[column].between(min_val, max_val)
def matches_pattern(column, pattern): return lambda df: df[column].str.match(pattern, na=False)

validator = DataValidator()

validator.add_rule(Rule("Unique custom IDs", unique_values('customer_id'), "Customer IDs must be unique across all records"))
validator.add_rule(Rule("Valid email format", matches_pattern('email', r'^[^@\s]+@[^@\s]+\.[^@\s]+$'), "Email addresses must contain @ symbol and domain"))
validator.add_rule(Rule("Reasonable custom age", between('age', 13, 120), "Customer age must be between 13 and 120 years"))
validator.add_rule(Rule("Non-negative spending", lambda df: df['total_spent'] >= 0, "Total spending amount cannot be negative"))

issues = validator.validate(customers)

for issue in issues:
  print(f"X Rule: {issue['rule']}")
  print(f"Problem: {issue['message']}")
  print(f"Affected rows: {issue['sample_rows']}\n")