-- 1. Top 5 funds by AUM
SELECT scheme_name, aum_crore 
FROM fact_performance 
ORDER BY aum_crore DESC 
LIMIT 5;

-- 2. Average NAV per month
SELECT amfi_code, strftime('%Y-%m', date) as month, AVG(nav) as avg_nav
FROM fact_nav
GROUP BY amfi_code, strftime('%Y-%m', date)
ORDER BY amfi_code, month;

-- 3. SIP YoY growth
SELECT 
    strftime('%Y', transaction_date) as year,
    SUM(amount_inr) as total_sip_amount,
    (SUM(amount_inr) - LAG(SUM(amount_inr)) OVER (ORDER BY strftime('%Y', transaction_date))) / LAG(SUM(amount_inr)) OVER (ORDER BY strftime('%Y', transaction_date)) * 100 as yoy_growth_pct
FROM fact_transactions
WHERE transaction_type = 'SIP'
GROUP BY strftime('%Y', transaction_date);

-- 4. Transactions by state
SELECT state, COUNT(transaction_id) as num_transactions, SUM(amount_inr) as total_volume
FROM fact_transactions
GROUP BY state
ORDER BY total_volume DESC;

-- 5. Funds with expense_ratio < 1%
SELECT amfi_code, scheme_name, expense_ratio_pct
FROM fact_performance
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;

-- 6. Total Redemption Amount by Age Group
SELECT age_group, SUM(amount_inr) as total_redemption
FROM fact_transactions
WHERE transaction_type = 'Redemption'
GROUP BY age_group
ORDER BY total_redemption DESC;

-- 7. Best performing Large Cap funds by 1yr return
SELECT p.scheme_name, p.return_1yr_pct
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE f.category = 'Large Cap'
ORDER BY p.return_1yr_pct DESC
LIMIT 5;

-- 8. Top 5 SIP investment cities
SELECT city, SUM(amount_inr) as total_sip
FROM fact_transactions
WHERE transaction_type = 'SIP'
GROUP BY city
ORDER BY total_sip DESC
LIMIT 5;

-- 9. Number of funds by Risk Grade
SELECT risk_grade, COUNT(amfi_code) as num_funds
FROM fact_performance
GROUP BY risk_grade
ORDER BY num_funds DESC;

-- 10. Average 3yr return by Fund House
SELECT fund_house, AVG(return_3yr_pct) as avg_3yr_return
FROM fact_performance
GROUP BY fund_house
ORDER BY avg_3yr_return DESC;
