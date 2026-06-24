/**
 * TGECET 2026 - College Allotment Finder
 * Search app for finding friends' college allotments
 */

(function () {
    'use strict';

    // State
    let allData = [];
    let filteredResults = [];
    let displayedCount = 0;
    const PAGE_SIZE = 30;
    let currentTab = 'name';
    let debounceTimer = null;

    // DOM Elements
    const nameSearch = document.getElementById('nameSearch');
    const rollSearch = document.getElementById('rollSearch');
    const collegeSearch = document.getElementById('collegeSearch');
    const clearName = document.getElementById('clearName');
    const clearRoll = document.getElementById('clearRoll');
    const clearCollege = document.getElementById('clearCollege');
    const resultsSection = document.getElementById('resultsSection');
    const resultsGrid = document.getElementById('resultsGrid');
    const resultsCount = document.getElementById('resultsCount');
    const emptyState = document.getElementById('emptyState');
    const loadingState = document.getElementById('loadingState');
    const resultsFooter = document.getElementById('resultsFooter');
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    const sortBy = document.getElementById('sortBy');
    const filterBranch = document.getElementById('filterBranch');
    const totalRecords = document.getElementById('totalRecords');
    const heroCount = document.getElementById('heroCount');
    const collegeChips = document.getElementById('collegeChips');

    // --- Data Loading ---
    async function loadData() {
        loadingState.style.display = 'block';
        try {
            const response = await fetch('allotment_data.json');
            if (!response.ok) throw new Error('Failed to load data');
            allData = await response.json();
            totalRecords.textContent = `${allData.length.toLocaleString()} Records`;
            heroCount.textContent = allData.length.toLocaleString() + '+';
            loadingState.style.display = 'none';
            populateCollegeChips();
            populateBranchFilter();
            console.log(`Loaded ${allData.length} records`);
        } catch (err) {
            loadingState.style.display = 'none';
            console.error('Error loading data:', err);
            totalRecords.textContent = 'Error loading';
        }
    }

    // --- College Chips ---
    function populateCollegeChips() {
        const colleges = new Map();
        allData.forEach(r => {
            if (!colleges.has(r.cc)) {
                colleges.set(r.cc, r.cn);
            }
        });

        const sorted = [...colleges.entries()].sort((a, b) => a[0].localeCompare(b[0]));
        collegeChips.innerHTML = '';
        sorted.forEach(([code, name]) => {
            const chip = document.createElement('button');
            chip.className = 'college-chip';
            chip.textContent = code;
            chip.title = name;
            chip.addEventListener('click', () => {
                document.querySelectorAll('.college-chip').forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
                collegeSearch.value = code;
                performSearch();
            });
            collegeChips.appendChild(chip);
        });
    }

    // --- Branch Filter ---
    function populateBranchFilter() {
        const branches = new Map();
        allData.forEach(r => {
            const code = r.bc || r.bn;
            if (code && !branches.has(code)) {
                branches.set(code, r.bn || r.bc);
            }
        });

        const sorted = [...branches.entries()].sort((a, b) => a[0].localeCompare(b[0]));
        sorted.forEach(([code, name]) => {
            const option = document.createElement('option');
            option.value = code;
            option.textContent = name.length > 30 ? code + ' - ' + name.substring(0, 30) + '...' : code + ' - ' + name;
            filterBranch.appendChild(option);
        });
    }

    // --- Search ---
    function performSearch() {
        const searchType = currentTab;
        let query = '';

        if (searchType === 'name') {
            query = nameSearch.value.trim().toLowerCase();
            clearName.style.display = query ? 'flex' : 'none';
            if (query.length < 2) {
                hideResults();
                return;
            }
        } else if (searchType === 'roll') {
            query = rollSearch.value.trim().toUpperCase();
            clearRoll.style.display = query ? 'flex' : 'none';
            if (query.length < 2) {
                hideResults();
                return;
            }
        } else if (searchType === 'college') {
            query = collegeSearch.value.trim().toLowerCase();
            if(clearCollege) clearCollege.style.display = query ? 'flex' : 'none';
            if (query.length < 2) {
                hideResults();
                return;
            }
        } else if (searchType === 'toppers') {
            // For toppers, no query is needed
        }

        // Filter data
        const selectedBranch = filterBranch.value;
        filteredResults = allData.filter(r => {
            let matchQuery = false;
            if (searchType === 'name') {
                matchQuery = r.name && r.name.toLowerCase().includes(query);
            } else if (searchType === 'roll') {
                matchQuery = r.ht && r.ht.toUpperCase().includes(query);
            } else if (searchType === 'college') {
                matchQuery = (r.cc && r.cc.toLowerCase().includes(query)) ||
                             (r.cn && r.cn.toLowerCase().includes(query));
            } else if (searchType === 'toppers') {
                matchQuery = true; // All records are considered, we'll sort and slice later
            }
            
            if (!matchQuery) return false;
            
            if (selectedBranch !== 'all') {
                const branchCode = r.bc || r.bn;
                if (branchCode !== selectedBranch) return false;
            }
            
            return true;
        });

        // Sort
        sortResults();

        // Display
        displayedCount = 0;
        resultsGrid.innerHTML = '';

        if (filteredResults.length === 0) {
            resultsSection.style.display = 'none';
            emptyState.style.display = 'block';
        } else {
            emptyState.style.display = 'none';
            resultsSection.style.display = 'block';
            resultsCount.textContent = filteredResults.length.toLocaleString();
            
            const resultsActions = document.querySelector('.results-actions');
            if (resultsActions) {
                resultsActions.style.display = 'flex';
                if (sortBy) {
                    sortBy.style.display = searchType === 'toppers' ? 'none' : 'block';
                }
            }
            
            updateCollegeAnalytics(searchType);
            showMoreResults();
        }
    }

    function updateCollegeAnalytics(searchType) {
        const analyticsDiv = document.getElementById('collegeAnalytics');
        if (searchType !== 'college' || filteredResults.length === 0) {
            if(analyticsDiv) analyticsDiv.style.display = 'none';
            return;
        }

        // Only show if all filtered results belong to the SAME college
        const firstCollegeCode = filteredResults[0].cc;
        const allSameCollege = filteredResults.every(r => r.cc === firstCollegeCode);
        
        if (!allSameCollege) {
            if(analyticsDiv) analyticsDiv.style.display = 'none';
            return;
        }

        if(analyticsDiv) analyticsDiv.style.display = 'block';
        
        document.getElementById('analyticsCollegeName').textContent = filteredResults[0].cn || 'Unknown College';
        document.getElementById('analyticsCollegeCode').textContent = firstCollegeCode;

        // Calculate Rank Cutoffs
        let minRank = Infinity;
        let maxRank = -Infinity;
        let maleCount = 0;
        let femaleCount = 0;
        const branchCounts = {};

        filteredResults.forEach(r => {
            const rank = parseInt(r.rank);
            if (!isNaN(rank)) {
                if (rank < minRank) minRank = rank;
                if (rank > maxRank) maxRank = rank;
            }

            const sex = (r.sex || '').toLowerCase();
            if (sex === 'm') maleCount++;
            else if (sex === 'f') femaleCount++;

            const branch = r.bc || r.bn || 'Unknown';
            branchCounts[branch] = (branchCounts[branch] || 0) + 1;
        });

        // Set Ranks
        if (minRank === Infinity) {
            document.getElementById('statCutoff').textContent = 'N/A';
        } else {
            document.getElementById('statCutoff').textContent = `${minRank} - ${maxRank}`;
        }

        // Set Top Branch
        let topBranch = 'N/A';
        let maxCount = 0;
        for (const [branch, count] of Object.entries(branchCounts)) {
            if (count > maxCount) {
                maxCount = count;
                topBranch = branch;
            }
        }
        document.getElementById('statTopBranch').textContent = topBranch;

        // Set Gender Ratio
        const totalGender = maleCount + femaleCount;
        if (totalGender > 0) {
            const mPct = Math.round((maleCount / totalGender) * 100);
            const fPct = 100 - mPct;
            document.getElementById('barMale').style.width = `${mPct}%`;
            document.getElementById('barFemale').style.width = `${fPct}%`;
            document.getElementById('statMale').textContent = `${mPct}%`;
            document.getElementById('statFemale').textContent = `${fPct}%`;
        } else {
            document.getElementById('barMale').style.width = `50%`;
            document.getElementById('barFemale').style.width = `50%`;
            document.getElementById('statMale').textContent = `50%`;
            document.getElementById('statFemale').textContent = `50%`;
        }
    }

    function sortResults() {
        if (currentTab === 'toppers') {
            filteredResults.sort((a, b) => {
                return (parseFloat(a.rank) || 99999) - (parseFloat(b.rank) || 99999);
            });
            return;
        }

        const criterion = sortBy.value;
        filteredResults.sort((a, b) => {
            if (criterion === 'name') return (a.name || '').localeCompare(b.name || '');
            if (criterion === 'rank') return (parseFloat(a.rank) || 99999) - (parseFloat(b.rank) || 99999);
            if (criterion === 'college') return (a.cn || '').localeCompare(b.cn || '');
            if (criterion === 'branch') return (a.bn || '').localeCompare(b.bn || '');
            return 0;
        });
    }

    function showMoreResults() {
        const currentPageSize = currentTab === 'toppers' ? 100 : PAGE_SIZE;
        const endIdx = Math.min(displayedCount + currentPageSize, filteredResults.length);
        const fragment = document.createDocumentFragment();

        if (currentTab === 'toppers') {
            if (displayedCount === 0) {
                resultsGrid.innerHTML = `
                    <div class="table-wrapper">
                        <table class="toppers-table">
                            <thead>
                                <tr>
                                    <th style="width: 80px;">Rank</th>
                                    <th>Name</th>
                                    <th>Hall Ticket</th>
                                    <th>Branch</th>
                                    <th>College Code</th>
                                </tr>
                            </thead>
                            <tbody id="toppersTbody"></tbody>
                        </table>
                    </div>
                `;
            }
            const tbody = document.getElementById('toppersTbody');
            for (let i = displayedCount; i < endIdx; i++) {
                const tr = createTableCard(filteredResults[i], i);
                fragment.appendChild(tr);
            }
            tbody.appendChild(fragment);
        } else {
            for (let i = displayedCount; i < endIdx; i++) {
                const card = createResultCard(filteredResults[i], i);
                fragment.appendChild(card);
            }
            resultsGrid.appendChild(fragment);
        }

        displayedCount = endIdx;

        if (displayedCount < filteredResults.length) {
            resultsFooter.style.display = 'block';
            loadMoreBtn.textContent = `Show More (${filteredResults.length - displayedCount} remaining)`;
        } else {
            resultsFooter.style.display = 'none';
        }
    }

    function createTableCard(record, index) {
        const tr = document.createElement('tr');
        tr.style.animation = 'fadeIn 0.3s ease';
        tr.style.animationDelay = `${(index % 100) * 10}ms`;
        tr.style.animationFillMode = 'both';

        tr.innerHTML = `
            <td class="rank-col">#${record.rank || 'N/A'}</td>
            <td class="name-col">${escapeHtml(record.name || 'N/A')}</td>
            <td class="mono-col">${escapeHtml(record.ht || 'N/A')}</td>
            <td>${escapeHtml(record.bn || record.bc || 'N/A')}</td>
            <td class="mono-col">${escapeHtml(record.cc || 'N/A')}</td>
        `;
        return tr;
    }

    function createResultCard(record, index) {
        const card = document.createElement('div');
        card.className = 'result-card';
        card.style.animationDelay = `${(index % PAGE_SIZE) * 30}ms`;

        const query = getActiveQuery();
        const highlightedName = highlightText(record.name || 'N/A', query, currentTab === 'name');
        const highlightedHT = highlightText(record.ht || 'N/A', query, currentTab === 'roll');
        const collegeCode = record.cc || '';
        const sexClass = (record.sex || '').toLowerCase() === 'f' ? 'female' : 'male';
        const sexLabel = (record.sex || '').toLowerCase() === 'f' ? '♀ Female' : '♂ Male';

        card.innerHTML = `
            <div class="card-top">
                <div class="card-name">${highlightedName}</div>
                <div class="card-rank">
                    <span>#</span>${record.rank || 'N/A'}
                </div>
            </div>
            <div class="card-college">
                <div class="college-icon">${collegeCode.substring(0, 2)}</div>
                <div class="college-info">
                    <div class="college-name">${record.cn || 'Unknown College'}</div>
                    <div class="branch-name">${record.bn || record.bc || 'Unknown Branch'}</div>
                </div>
            </div>
            <div class="card-details">
                <div class="detail-item">
                    <span class="detail-label">Hall Ticket</span>
                    <span class="detail-value">${highlightedHT}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Gender</span>
                    <span class="sex-badge ${sexClass}">${sexLabel}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Caste / Region</span>
                    <span class="detail-value">${record.caste || 'N/A'} / ${record.region || 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Seat Category</span>
                    <span class="seat-badge">${record.seat_cat || 'N/A'}</span>
                </div>
            </div>
            <div class="card-actions">
                <button class="share-btn" onclick="window.handleShare(this, '${escapeRegex(record.name || 'Student').replace(/'/g, "\\'")}')">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path><polyline points="16 6 12 2 8 6"></polyline><line x1="12" y1="2" x2="12" y2="15"></line>
                    </svg>
                    Share Result
                </button>
            </div>
        `;

        return card;
    }

    window.handleShare = async function(button, name) {
        const card = button.closest('.result-card');
        button.style.display = 'none'; // hide share button during capture
        
        // Add watermark
        const watermark = document.createElement('div');
        watermark.className = 'card-watermark';
        watermark.innerHTML = '🔍 Found via TGECET Finder by <b>@VIRUS_BOSS</b>';
        card.appendChild(watermark);

        // Add confetti!
        if (window.confetti) {
            confetti({
                particleCount: 100,
                spread: 70,
                origin: { y: 0.6 },
                colors: ['#6366f1', '#8b5cf6', '#06b6d4', '#22c55e']
            });
        }

        try {
            const canvas = await html2canvas(card, {
                backgroundColor: '#141420', // var(--bg-card)
                scale: 2,
                logging: false,
                useCORS: true
            });
            
            const link = document.createElement('a');
            link.download = `TGECET_Result_${name.replace(/\s+/g, '_')}.png`;
            link.href = canvas.toDataURL('image/png');
            link.click();
        } catch (err) {
            console.error('Error generating image:', err);
            alert('Failed to generate shareable image.');
        } finally {
            if(card.contains(watermark)) {
                card.removeChild(watermark);
            }
            button.style.display = 'flex'; // restore share button
        }
    };

    function highlightText(text, query, shouldHighlight) {
        if (!shouldHighlight || !query || query.length < 2) return escapeHtml(text);
        const escaped = escapeHtml(text);
        const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
        return escaped.replace(regex, '<span class="highlight">$1</span>');
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    function escapeRegex(str) {
        return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    function getActiveQuery() {
        if (currentTab === 'name') return nameSearch.value.trim();
        if (currentTab === 'roll') return rollSearch.value.trim();
        if (currentTab === 'college') return collegeSearch.value.trim();
        return '';
    }

    function hideResults() {
        resultsSection.style.display = 'none';
        emptyState.style.display = 'none';
    }

    // --- Tab Switching ---
    function switchTab(tab) {
        currentTab = tab;
        document.querySelectorAll('.search-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.search-panel').forEach(p => p.classList.remove('active'));

        document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
        document.getElementById(`panel${tab.charAt(0).toUpperCase() + tab.slice(1)}`).classList.add('active');

        hideResults();

        if (tab === 'toppers') {
            performSearch();
        } else {
            // Auto-focus the input
            setTimeout(() => {
                if (tab === 'name') nameSearch.focus();
                else if (tab === 'roll') rollSearch.focus();
                else if (tab === 'college') collegeSearch.focus();
            }, 100);
        }
    }

    // --- Event Listeners ---
    function init() {
        // Tab clicks
        document.querySelectorAll('.search-tab').forEach(tab => {
            tab.addEventListener('click', () => switchTab(tab.dataset.tab));
        });

        // Search inputs with debounce
        [nameSearch, rollSearch, collegeSearch].forEach(input => {
            input.addEventListener('input', () => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(performSearch, 200);
            });
        });

        // Enter key
        [nameSearch, rollSearch, collegeSearch].forEach(input => {
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    clearTimeout(debounceTimer);
                    performSearch();
                }
            });
        });

        // Clear buttons
        clearName.addEventListener('click', () => {
            nameSearch.value = '';
            clearName.style.display = 'none';
            hideResults();
            nameSearch.focus();
        });

        clearRoll.addEventListener('click', () => {
            rollSearch.value = '';
            clearRoll.style.display = 'none';
            hideResults();
            rollSearch.focus();
        });

        clearCollege.addEventListener('click', () => {
            collegeSearch.value = '';
            clearCollege.style.display = 'none';
            document.querySelectorAll('.college-chip').forEach(c => c.classList.remove('active'));
            hideResults();
            collegeSearch.focus();
        });

        // Sort change
        sortBy.addEventListener('change', () => {
            if (filteredResults.length > 0) {
                sortResults();
                displayedCount = 0;
                resultsGrid.innerHTML = '';
                showMoreResults();
            }
        });

        // Filter change
        filterBranch.addEventListener('change', () => {
            if (currentTab === 'name' && nameSearch.value.trim().length >= 2) performSearch();
            else if (currentTab === 'roll' && rollSearch.value.trim().length >= 2) performSearch();
            else if (currentTab === 'college' && collegeSearch.value.trim().length >= 2) performSearch();
        });

        // Load more
        loadMoreBtn.addEventListener('click', showMoreResults);

        // Keyboard shortcut: / to focus search
        document.addEventListener('keydown', (e) => {
            if (e.key === '/' && document.activeElement.tagName !== 'INPUT') {
                e.preventDefault();
                if (currentTab === 'name') nameSearch.focus();
                else if (currentTab === 'roll') rollSearch.focus();
                else if (currentTab === 'college') collegeSearch.focus();
            }
        });

        // GitHub Banner Confetti
        const ghBtn = document.querySelector('.gh-btn');
        if (ghBtn) {
            ghBtn.addEventListener('click', (e) => {
                if (window.confetti) {
                    confetti({
                        particleCount: 150,
                        spread: 100,
                        origin: { y: 0.9 },
                        zIndex: 2000
                    });
                }
            });
        }

        // Theme Toggle Logic
        const themeToggle = document.getElementById('themeToggle');
        const sunIcon = document.querySelector('.sun-icon');
        const moonIcon = document.querySelector('.moon-icon');

        function setTheme(theme) {
            if (theme === 'light') {
                document.documentElement.classList.add('light-mode');
                if(sunIcon) sunIcon.style.display = 'none';
                if(moonIcon) moonIcon.style.display = 'block';
                localStorage.setItem('theme', 'light');
            } else {
                document.documentElement.classList.remove('light-mode');
                if(sunIcon) sunIcon.style.display = 'block';
                if(moonIcon) moonIcon.style.display = 'none';
                localStorage.setItem('theme', 'dark');
            }
        }

        // Initialize theme from storage or default to dark
        const savedTheme = localStorage.getItem('theme') || 'dark';
        setTheme(savedTheme);

        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                const currentTheme = document.documentElement.classList.contains('light-mode') ? 'light' : 'dark';
                setTheme(currentTheme === 'dark' ? 'light' : 'dark');
            });
        }

        // Load data
        loadData();
    }

    // Start
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Register Service Worker for PWA
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('sw.js').then(registration => {
                console.log('SW registered: ', registration);
            }).catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
        });
    }
})();
