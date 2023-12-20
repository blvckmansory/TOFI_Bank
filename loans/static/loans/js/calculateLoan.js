function calculateLoan() {
            var issue_amount = parseFloat(document.getElementById('loanAmount').value);
            var months = parseFloat(document.getElementById('loanTerm').value);
            var currency = document.getElementById('id_currency_loan').value;

            var loanType = document.getElementById('id_loan_type').value;
            var procent = getInterestRate(loanType);

            var monthlyInterestRate = procent / 100 / 12;
            var totalInterest = monthlyInterestRate * months * issue_amount;
            var totalPayment = issue_amount + totalInterest;
            var monthlyPayment = totalPayment / months;

            document.getElementById('totalPayment').innerHTML = 'Общая сумма выплаты: ' + totalPayment + ' ' + currency;
            document.getElementById('procent').innerHTML = 'Проценты годовых: ' + procent + '%';
            document.getElementById('monthlyPayment').innerHTML = 'Ежемесячный платеж: ' + monthlyPayment.toFixed(2) + ' ' + currency;

        }

        function getInterestRate(loanType) {
                if (loanType === 'Consumer_loan') {
                        return 15.25;
                } else if (loanType === 'Mortgage_loan') {
                        return 12.5;
                } else if (loanType === 'Auto_loan') {
                        return 9.5;
                } else {
                        return 0;
                }
        }