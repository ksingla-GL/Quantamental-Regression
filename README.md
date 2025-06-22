# Quantamental-Regression

This repo implements a quantamental regression strategy that dynamically constructs composite factor scores (Momentum, Reversal, Volatility) via rolling OLS, then forms long/short portfolios based on cross‑sectional ranking. The framework supports modular data ingestion, signal generation, portfolio construction, and performance evaluation (Sharpe, annualized return, max drawdown).

Some additional fixes before being made live -;
1. A small Ridge/decay‐factor smoothing was added for regularizing the regression
2. Instead of equal‐weighting each of the top 100, we weighted by the magnitude of their inverse volatility
3. Long/short legs were Beta‐neutralized so we are not making big industry bets
