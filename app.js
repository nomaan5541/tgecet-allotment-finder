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
            clearCollege.style.display = query ? 'flex' : 'none';
            if (query.length < 2) {
                hideResults();
                return;
            }
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
            showMoreResults();
        }
    }

    function sortResults() {
        const criterion = sortBy.value;
        filteredResults.sort((a, b) => {
            if (criterion === 'name') return (a.name || '').localeCompare(b.name || '');
            if (criterion === 'rank') return (parseInt(a.rank) || 99999) - (parseInt(b.rank) || 99999);
            if (criterion === 'college') return (a.cn || '').localeCompare(b.cn || '');
            if (criterion === 'branch') return (a.bn || '').localeCompare(b.bn || '');
            return 0;
        });
    }

    function showMoreResults() {
        const endIdx = Math.min(displayedCount + PAGE_SIZE, filteredResults.length);
        const fragment = document.createDocumentFragment();

        for (let i = displayedCount; i < endIdx; i++) {
            const card = createResultCard(filteredResults[i], i);
            fragment.appendChild(card);
        }

        resultsGrid.appendChild(fragment);
        displayedCount = endIdx;

        if (displayedCount < filteredResults.length) {
            resultsFooter.style.display = 'block';
            loadMoreBtn.textContent = `Show More (${filteredResults.length - displayedCount} remaining)`;
        } else {
            resultsFooter.style.display = 'none';
        }
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
        `;

        return card;
    }

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

        // Auto-focus the input
        setTimeout(() => {
            if (tab === 'name') nameSearch.focus();
            else if (tab === 'roll') rollSearch.focus();
            else if (tab === 'college') collegeSearch.focus();
        }, 100);
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

        // Load data
        loadData();
    }

    // Start
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
