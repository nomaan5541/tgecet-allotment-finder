(function () {
    'use strict';

    // Theme logic
    const themeToggle = document.getElementById('themeToggle');
    function setTheme(theme) {
        if (theme === 'light') {
            document.documentElement.classList.add('light-mode');
            localStorage.setItem('theme', 'light');
            if(themeToggle) {
                themeToggle.querySelector('.sun-icon').style.display = 'none';
                themeToggle.querySelector('.moon-icon').style.display = 'block';
            }
        } else {
            document.documentElement.classList.remove('light-mode');
            localStorage.setItem('theme', 'dark');
            if(themeToggle) {
                themeToggle.querySelector('.sun-icon').style.display = 'block';
                themeToggle.querySelector('.moon-icon').style.display = 'none';
            }
        }
    }
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.classList.contains('light-mode') ? 'light' : 'dark';
            setTheme(currentTheme === 'dark' ? 'light' : 'dark');
        });
    }

    // Predictor logic
    let allData = [];
    const btnPredict = document.getElementById('btnPredict');
    const loadingPredictor = document.getElementById('loadingPredictor');
    const resultsPredictor = document.getElementById('resultsPredictor');
    const predList = document.getElementById('predList');
    const predCount = document.getElementById('predCount');

    // Load data lazily
    async function getData() {
        if (allData.length > 0) return allData;
        const response = await fetch('allotment_data.json');
        if (!response.ok) throw new Error('Failed to load data');
        allData = await response.json();
        return allData;
    }

    function isEligible(seatCat, userCat, userGender) {
        if (!seatCat) return false;
        seatCat = seatCat.toUpperCase();

        // Male cannot take Girls seats
        if (userGender === 'M' && seatCat.includes('GIRLS')) {
            return false;
        }

        // Everyone is eligible for Open Category (OC) seats
        if (seatCat.includes('OC_')) return true;

        // SC/ST matching (SC can be SC_I, SC_II, SC_III etc in the data)
        if (userCat === 'SC' && seatCat.includes('SC_')) return true;
        if (userCat === 'ST' && seatCat.includes('ST_')) return true;

        // BC matching
        if (seatCat.includes(userCat + '_')) return true;

        return false;
    }

    async function predictChances() {
        const rankInput = document.getElementById('predRank').value;
        const userCat = document.getElementById('predCat').value;
        const userGender = document.getElementById('predGender').value;

        if (!rankInput || rankInput <= 0) {
            alert('Please enter a valid rank.');
            return;
        }

        const userRank = parseFloat(rankInput);

        btnPredict.disabled = true;
        resultsPredictor.style.display = 'none';
        loadingPredictor.style.display = 'block';

        try {
            const data = await getData();

            // Group by college and branch to find max rank (cutoff)
            // Key: "cc|bc", Value: { cn, bn, cutoffRank }
            const cutoffs = {};

            for (const record of data) {
                const rank = parseFloat(record.rank);
                if (isNaN(rank)) continue;

                const seatCat = record.seat_cat || '';
                
                if (isEligible(seatCat, userCat, userGender)) {
                    const key = `${record.cc}|${record.bc}`;
                    if (!cutoffs[key] || rank > cutoffs[key].cutoffRank) {
                        cutoffs[key] = {
                            cc: record.cc,
                            cn: record.cn || record.cc,
                            bc: record.bc,
                            bn: record.bn || record.bc,
                            cutoffRank: rank
                        };
                    }
                }
            }

            // Filter where userRank <= cutoffRank
            const chances = Object.values(cutoffs).filter(c => userRank <= c.cutoffRank);

            // Sort by cutoff rank ascending (harder to get first)
            chances.sort((a, b) => a.cutoffRank - b.cutoffRank);

            // Render
            predCount.textContent = chances.length;
            predList.innerHTML = '';

            if (chances.length === 0) {
                predList.innerHTML = `<p style="color:var(--text-secondary); text-align:center; padding: 20px;">No colleges found based on previous year data for your rank and category.</p>`;
            } else {
                chances.forEach(chance => {
                    const div = document.createElement('div');
                    div.className = 'predicted-item';
                    
                    const cnClean = chance.cn.includes(' - ') ? chance.cn.split(' - ')[1] : chance.cn;
                    
                    div.innerHTML = `
                        <div>
                            <div class="pred-college">${cnClean} (${chance.cc})</div>
                            <div class="pred-branch">${chance.bn}</div>
                        </div>
                        <div class="pred-cutoff">Max Cutoff: ${chance.cutoffRank.toFixed(0)}</div>
                    `;
                    predList.appendChild(div);
                });
            }

            loadingPredictor.style.display = 'none';
            resultsPredictor.style.display = 'block';

        } catch (err) {
            console.error('Error predicting:', err);
            alert('An error occurred while predicting. Please try again.');
            loadingPredictor.style.display = 'none';
        } finally {
            btnPredict.disabled = false;
        }
    }

    btnPredict.addEventListener('click', predictChances);

})();
