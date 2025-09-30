
        function changeCalcType() {
            document.getElementById('result').innerHTML = '';
        }

        function calculateMRV() {
            const trees = parseFloat(document.getElementById('trees').value) || 0;
            const area = parseFloat(document.getElementById('area').value) || 0;
            const survivalRate = parseFloat(document.getElementById('survivalRate').value) || 100;
            const years = parseFloat(document.getElementById('years').value) || 1;
            const treeCost = parseFloat(document.getElementById('treeCost').value) || 0;
            const maintenanceCost = parseFloat(document.getElementById('maintenanceCost').value) || 0;
            const govIncentive = parseFloat(document.getElementById('govIncentive').value) || 0;
            const drone = document.getElementById('droneData').value;
            const community = document.getElementById('community').value;
            const ecosystem = document.getElementById('ecosystem').value;
            const calcType = document.getElementById('calcType').value;

            let ecoFactor = 1;
            switch (ecosystem) {
                case 'mangrove': ecoFactor = 1.8; break;
                case 'seagrass': ecoFactor = 1.2; break;
                case 'saltmarsh': ecoFactor = 1.4; break;
                case 'mudflat': ecoFactor = 0.8; break;
                case 'coastalForest': ecoFactor = 2.0; break;
            }

            const survivedTrees = trees * (survivalRate / 100);
            const o2PerCO2 = 0.73;
            let resultText = '';

            if (calcType === 'yearlyCredits') {
                let totalCO2 = 0, totalO2 = 0, yearlyData = [];
                for (let i = 1; i <= years; i++) {
                    let co2Year = survivedTrees * ecoFactor;
                    let o2Year = co2Year * o2PerCO2;
                    yearlyData.push(`Year ${i}: CO₂ Gained: ${co2Year.toFixed(2)} t, O₂ Released: ${o2Year.toFixed(2)} t`);
                    totalCO2 += co2Year;
                    totalO2 += o2Year;
                }
                resultText = `<h3>Total CO₂: ${totalCO2.toFixed(2)} t | Total O₂: ${totalO2.toFixed(2)} t</h3><p>${yearlyData.join('<br>')}</p>`;
            } else if (calcType === 'co2Released') {
                const totalCO2 = survivedTrees * ecoFactor * years;
                resultText = `<h3>Estimated CO₂ Released: ${totalCO2.toFixed(2)} t</h3>`;
            } else if (calcType === 'requiredTrees') {
                const co2Target = parseFloat(prompt("Enter target CO₂ (t):")) || 0;
                const reqTrees = co2Target / ecoFactor;
                resultText = `<h3>Required Trees: ${Math.ceil(reqTrees)}</h3>`;
            } else if (calcType === 'tokenizedCredits') {
                const totalCredits = survivedTrees * ecoFactor;
                resultText = `<h3>Tokenized Credits: ${Math.floor(totalCredits*100)} Tokens</h3>`;
            } else if (calcType === 'costAnalysis') {
                const totalCost = (trees * treeCost) + (maintenanceCost * years) - govIncentive;
                resultText = `<h3>Total Project Cost: ₹${totalCost.toFixed(2)}</h3>`;
            } else if (calcType === 'mrvScore') {
                let score = 50;
                if (drone === 'yes') score += 20;
                if (community === 'high') score += 20;
                if (survivalRate > 80) score += 10;
                resultText = `<h3>MRV Verification Score: ${score}/100</h3>`;
            }

            const resultDiv = document.getElementById('result');
            resultDiv.style.opacity = 0;
            setTimeout(() => {
                resultDiv.innerHTML = resultText;
                resultDiv.style.opacity = 1;
            }, 200);
        }
