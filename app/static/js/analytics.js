/**
 * Analytics Dashboard JavaScript
 * Handles data visualization, chart interactions, and time period controls
 */

class AnalyticsDashboard {
    constructor() {
        this.charts = {};
        this.currentData = null;
        this.currentPeriod = 12;
        this.currentYear = new Date().getFullYear();
        
        // Chart color schemes
        this.colors = {
            primary: '#55970f',
            secondary: '#6abe11',
            accent: '#8DC63F',
            light: '#A3E635',
            success: '#10B981',
            warning: '#F59E0B',
            error: '#EF4444',
            info: '#3B82F6',
            gray: '#6B7280'
        };
        
        this.chartColors = [
            '#55970f', '#6abe11', '#8DC63F', '#A3E635', '#10B981',
            '#F59E0B', '#EF4444', '#3B82F6', '#8B5CF6', '#EC4899'
        ];
        
        // Initialize table pagination state
        this.tablePagination = {
            category: { currentPage: 1, itemsPerPage: 10, showAll: false },
            store: { currentPage: 1, itemsPerPage: 10, showAll: false }
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.populateYearSelector();
        this.loadAnalyticsData();
    }
    
    setupEventListeners() {
        // Time period controls
        document.getElementById('period-select').addEventListener('change', (e) => {
            this.currentPeriod = parseInt(e.target.value);
            this.loadAnalyticsData();
        });
        
        document.getElementById('year-select').addEventListener('change', (e) => {
            this.currentYear = parseInt(e.target.value);
            this.loadAnalyticsData();
        });
        
        document.getElementById('refresh-analytics').addEventListener('click', () => {
            this.loadAnalyticsData();
        });
        
        // Chart type toggles
        this.setupChartTypeToggles();
        
        // Fullscreen buttons
        this.setupFullscreenButtons();
        
        // Table controls
        this.setupTableControls();
    }
    
    setupChartTypeToggles() {
        const toggles = [
            { id: 'trends-chart-type', chartId: 'spending-trends-chart', types: ['line', 'bar'] },
            { id: 'category-chart-type', chartId: 'category-chart', types: ['pie', 'doughnut', 'bar'] },
            { id: 'store-chart-type', chartId: 'store-chart', types: ['bar', 'horizontalBar', 'pie'] },
            { id: 'monthly-chart-type', chartId: 'monthly-chart', types: ['bar', 'line'] }
        ];
        
        toggles.forEach(toggle => {
            const button = document.getElementById(toggle.id);
            if (button) {
                button.addEventListener('click', () => {
                    this.toggleChartType(toggle.chartId, toggle.types);
                    this.updateToggleButton(button, toggle.types);
                });
            }
        });
    }
    
    setupFullscreenButtons() {
        const fullscreenButtons = [
            { id: 'trends-fullscreen', chartId: 'spending-trends-chart', title: 'Spending Trends' },
            { id: 'category-fullscreen', chartId: 'category-chart', title: 'Spending by Category' },
            { id: 'store-fullscreen', chartId: 'store-chart', title: 'Top Stores' },
            { id: 'monthly-fullscreen', chartId: 'monthly-chart', title: 'Monthly Spending' }
        ];
        
        fullscreenButtons.forEach(button => {
            const element = document.getElementById(button.id);
            if (element) {
                element.addEventListener('click', () => {
                    this.openFullscreenChart(button.chartId, button.title);
                });
            }
        });
    }
    
    setupTableControls() {
        // Category table controls
        const categoryToggle = document.getElementById('category-table-toggle');
        const categoryExport = document.getElementById('category-export');
        
        if (categoryToggle) {
            categoryToggle.addEventListener('click', () => {
                this.toggleTableView('category');
            });
        }
        
        if (categoryExport) {
            categoryExport.addEventListener('click', () => {
                this.exportTableData('category');
            });
        }
        
        // Store table controls
        const storeToggle = document.getElementById('store-table-toggle');
        const storeExport = document.getElementById('store-export');
        
        if (storeToggle) {
            storeToggle.addEventListener('click', () => {
                this.toggleTableView('store');
            });
        }
        
        if (storeExport) {
            storeExport.addEventListener('click', () => {
                this.exportTableData('store');
            });
        }
    }
    
    updateToggleButton(button, types) {
        const currentType = button.dataset.currentType || types[0];
        const currentIndex = types.indexOf(currentType);
        const nextIndex = (currentIndex + 1) % types.length;
        const nextType = types[nextIndex];
        
        button.dataset.currentType = nextType;
        
        // Update button text and icon
        const icons = {
            line: 'fas fa-chart-line',
            bar: 'fas fa-chart-bar',
            pie: 'fas fa-chart-pie',
            doughnut: 'fas fa-chart-pie',
            horizontalBar: 'fas fa-chart-bar'
        };
        
        const labels = {
            line: 'Line',
            bar: 'Bar',
            pie: 'Pie',
            doughnut: 'Doughnut',
            horizontalBar: 'Horizontal'
        };
        
        button.innerHTML = `<i class="${icons[nextType]} mr-1"></i>${labels[nextType]}`;
    }
    
    populateYearSelector() {
        const yearSelect = document.getElementById('year-select');
        const currentYear = new Date().getFullYear();
        
        // Add years from current year back to 5 years ago
        for (let year = currentYear; year >= currentYear - 5; year--) {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            if (year === currentYear) option.selected = true;
            yearSelect.appendChild(option);
        }
    }
    
    async loadAnalyticsData() {
        this.showLoading();
        
        try {
            const response = await fetch(`/api/analytics/comprehensive?period=${this.currentPeriod}&year=${this.currentYear}`);
            if (!response.ok) throw new Error('Failed to load analytics data');
            
            this.currentData = await response.json();
            this.renderAnalytics();
        } catch (error) {
            console.error('Error loading analytics:', error);
            this.showError('Failed to load analytics data. Please try again.');
        } finally {
            this.hideLoading();
        }
    }
    
    showLoading() {
        document.getElementById('analytics-loading').classList.remove('hidden');
        document.getElementById('analytics-content').style.opacity = '0.5';
    }
    
    hideLoading() {
        document.getElementById('analytics-loading').classList.add('hidden');
        document.getElementById('analytics-content').style.opacity = '1';
    }
    
    showError(message) {
        // Create or update error message
        let errorDiv = document.getElementById('analytics-error');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'analytics-error';
            errorDiv.className = 'bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4';
            document.getElementById('analytics-content').prepend(errorDiv);
        }
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
    }
    
    renderAnalytics() {
        if (!this.currentData) return;
        
        this.updateSummaryCards();
        this.renderSpendingTrendsChart();
        this.renderCategoryChart();
        this.renderStoreChart();
        this.renderMonthlyChart();
        this.updateDataTables();
    }
    
    updateSummaryCards() {
        const { spending_trends, category_analysis, store_analysis } = this.currentData;
        
        // Total spending
        const totalSpending = spending_trends.statistics.total_spending || 0;
        document.getElementById('total-spending').textContent = this.formatCurrency(totalSpending);
        
        // Average monthly spending
        const avgMonthly = spending_trends.statistics.avg_monthly_spending || 0;
        document.getElementById('avg-monthly').textContent = this.formatCurrency(avgMonthly);
        
        // Total purchases
        const totalPurchases = spending_trends.trends_data.reduce((sum, item) => sum + item.purchase_count, 0);
        document.getElementById('total-purchases').textContent = totalPurchases.toLocaleString();
        
        // Spending trend
        const trendDirection = spending_trends.statistics.trend_direction || 'stable';
        const trendElement = document.getElementById('spending-trend');
        trendElement.textContent = this.formatTrendText(trendDirection);
        trendElement.className = `text-3xl font-bold ${this.getTrendColor(trendDirection)}`;
    }
    
    formatTrendText(direction) {
        const trends = {
            increasing: 'Rising',
            decreasing: 'Falling',
            stable: 'Stable'
        };
        return trends[direction] || 'Stable';
    }
    
    getTrendColor(direction) {
        const colors = {
            increasing: 'text-green-600',
            decreasing: 'text-red-600',
            stable: 'text-gray-600'
        };
        return colors[direction] || 'text-gray-600';
    }
    
    renderSpendingTrendsChart() {
        const ctx = document.getElementById('spending-trends-chart').getContext('2d');
        const { trends_data } = this.currentData.spending_trends;
        
        // Destroy existing chart
        if (this.charts.trendsChart) {
            this.charts.trendsChart.destroy();
        }
        
        const chartType = document.getElementById('trends-chart-type').dataset.currentType || 'line';
        
        this.charts.trendsChart = new Chart(ctx, {
            type: chartType,
            data: {
                labels: trends_data.map(item => item.period),
                datasets: [{
                    label: 'Spending',
                    data: trends_data.map(item => item.total_spending),
                    backgroundColor: chartType === 'line' ? 'rgba(85, 151, 15, 0.1)' : this.colors.primary,
                    borderColor: this.colors.primary,
                    borderWidth: 2,
                    fill: chartType === 'line',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const value = this.formatCurrency(context.parsed.y);
                                const dataPoint = trends_data[context.dataIndex];
                                return [
                                    `Spending: ${value}`,
                                    `Purchases: ${dataPoint.purchase_count}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: (value) => this.formatCurrency(value)
                        }
                    }
                }
            }
        });
    }
    
    renderCategoryChart() {
        const ctx = document.getElementById('category-chart').getContext('2d');
        const { category_analysis } = this.currentData.category_analysis;
        
        // Destroy existing chart
        if (this.charts.categoryChart) {
            this.charts.categoryChart.destroy();
        }
        
        const chartType = document.getElementById('category-chart-type').dataset.currentType || 'pie';
        const topCategories = category_analysis.slice(0, 10); // Show top 10 categories
        
        this.charts.categoryChart = new Chart(ctx, {
            type: chartType,
            data: {
                labels: topCategories.map(item => item.category),
                datasets: [{
                    data: topCategories.map(item => item.total_spending),
                    backgroundColor: this.chartColors.slice(0, topCategories.length),
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: chartType === 'bar' ? 'top' : 'right',
                        labels: {
                            generateLabels: (chart) => {
                                const data = chart.data;
                                return data.labels.map((label, index) => ({
                                    text: `${label} (${topCategories[index].percentage}%)`,
                                    fillStyle: data.datasets[0].backgroundColor[index],
                                    strokeStyle: data.datasets[0].borderColor,
                                    lineWidth: data.datasets[0].borderWidth
                                }));
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const category = topCategories[context.dataIndex];
                                return [
                                    `${category.category}: ${this.formatCurrency(category.total_spending)}`,
                                    `Items: ${category.purchase_count}`,
                                    `Percentage: ${category.percentage}%`
                                ];
                            }
                        }
                    }
                },
                scales: chartType === 'bar' ? {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: (value) => this.formatCurrency(value)
                        }
                    }
                } : {}
            }
        });
    }
    
    renderStoreChart() {
        const ctx = document.getElementById('store-chart').getContext('2d');
        const { store_analysis } = this.currentData.store_analysis;
        
        // Destroy existing chart
        if (this.charts.storeChart) {
            this.charts.storeChart.destroy();
        }
        
        const chartType = document.getElementById('store-chart-type').dataset.currentType || 'bar';
        const topStores = store_analysis.slice(0, 10); // Show top 10 stores
        
        this.charts.storeChart = new Chart(ctx, {
            type: chartType === 'horizontalBar' ? 'bar' : chartType,
            data: {
                labels: topStores.map(item => item.store_name),
                datasets: [{
                    label: 'Spending',
                    data: topStores.map(item => item.total_spending),
                    backgroundColor: chartType === 'pie' ? this.chartColors.slice(0, topStores.length) : this.colors.secondary,
                    borderColor: chartType === 'pie' ? '#ffffff' : this.colors.primary,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: chartType === 'horizontalBar' ? 'y' : 'x',
                plugins: {
                    legend: {
                        display: chartType === 'pie',
                        position: 'right'
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const store = topStores[context.dataIndex];
                                return [
                                    `${store.store_name}: ${this.formatCurrency(store.total_spending)}`,
                                    `Items: ${store.purchase_count}`,
                                    `Percentage: ${store.percentage}%`
                                ];
                            }
                        }
                    }
                },
                scales: chartType !== 'pie' ? {
                    [chartType === 'horizontalBar' ? 'x' : 'y']: {
                        beginAtZero: true,
                        ticks: {
                            callback: (value) => this.formatCurrency(value)
                        }
                    }
                } : {}
            }
        });
    }
    
    renderMonthlyChart() {
        const ctx = document.getElementById('monthly-chart').getContext('2d');
        const { monthly_spending } = this.currentData.monthly_spending;
        
        // Destroy existing chart
        if (this.charts.monthlyChart) {
            this.charts.monthlyChart.destroy();
        }
        
        const chartType = document.getElementById('monthly-chart-type').dataset.currentType || 'bar';
        const recentMonths = monthly_spending.slice(0, 12); // Show last 12 months
        
        this.charts.monthlyChart = new Chart(ctx, {
            type: chartType,
            data: {
                labels: recentMonths.map(item => item.period),
                datasets: [{
                    label: 'Monthly Spending',
                    data: recentMonths.map(item => item.total_spending),
                    backgroundColor: chartType === 'line' ? 'rgba(139, 198, 63, 0.1)' : this.colors.accent,
                    borderColor: this.colors.accent,
                    borderWidth: 2,
                    fill: chartType === 'line',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const month = recentMonths[context.dataIndex];
                                return [
                                    `Spending: ${this.formatCurrency(month.total_spending)}`,
                                    `Purchases: ${month.purchase_count}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: (value) => this.formatCurrency(value)
                        }
                    }
                }
            }
        });
    }
    
    toggleChartType(chartId, types) {
        const chart = this.charts[this.getChartKey(chartId)];
        if (!chart) return;
        
        const button = document.querySelector(`[data-chart="${chartId}"]`) || 
                      document.getElementById(chartId.replace('-chart', '-chart-type'));
        const currentType = button.dataset.currentType || types[0];
        const currentIndex = types.indexOf(currentType);
        const nextType = types[(currentIndex + 1) % types.length];
        
        button.dataset.currentType = nextType;
        
        // Re-render the specific chart
        switch (chartId) {
            case 'spending-trends-chart':
                this.renderSpendingTrendsChart();
                break;
            case 'category-chart':
                this.renderCategoryChart();
                break;
            case 'store-chart':
                this.renderStoreChart();
                break;
            case 'monthly-chart':
                this.renderMonthlyChart();
                break;
        }
    }
    
    getChartKey(chartId) {
        const mapping = {
            'spending-trends-chart': 'trendsChart',
            'category-chart': 'categoryChart',
            'store-chart': 'storeChart',
            'monthly-chart': 'monthlyChart'
        };
        return mapping[chartId];
    }
    
    updateDataTables() {
        this.updateCategoryTable();
        this.updateStoreTable();
    }
    
    updateCategoryTable() {
        const tbody = document.getElementById('category-table-body');
        const { category_analysis } = this.currentData.category_analysis;
        const pagination = this.tablePagination.category;
        
        tbody.innerHTML = '';
        
        // Determine which items to show
        let itemsToShow = category_analysis;
        if (!pagination.showAll) {
            const startIndex = (pagination.currentPage - 1) * pagination.itemsPerPage;
            const endIndex = startIndex + pagination.itemsPerPage;
            itemsToShow = category_analysis.slice(startIndex, endIndex);
        }
        
        itemsToShow.forEach(category => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="px-3 lg:px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    ${category.category}
                </td>
                <td class="px-3 lg:px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${this.formatCurrency(category.total_spending)}
                </td>
                <td class="px-3 lg:px-6 py-4 whitespace-nowrap text-sm text-gray-500 hidden sm:table-cell">
                    ${category.purchase_count}
                </td>
                <td class="px-3 lg:px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div class="flex items-center">
                        <div class="w-12 lg:w-16 bg-gray-200 rounded-full h-2 mr-2">
                            <div class="bg-green-600 h-2 rounded-full" style="width: ${category.percentage}%"></div>
                        </div>
                        <span class="text-xs lg:text-sm">${category.percentage}%</span>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
        
        // Update pagination info
        this.updateTablePagination('category', category_analysis.length);
    }
    
    updateStoreTable() {
        const tbody = document.getElementById('store-table-body');
        const { store_analysis } = this.currentData.store_analysis;
        const pagination = this.tablePagination.store;
        
        tbody.innerHTML = '';
        
        // Determine which items to show
        let itemsToShow = store_analysis;
        if (!pagination.showAll) {
            const startIndex = (pagination.currentPage - 1) * pagination.itemsPerPage;
            const endIndex = startIndex + pagination.itemsPerPage;
            itemsToShow = store_analysis.slice(startIndex, endIndex);
        }
        
        itemsToShow.forEach(store => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="px-3 lg:px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    ${store.store_name}
                </td>
                <td class="px-3 lg:px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${this.formatCurrency(store.total_spending)}
                </td>
                <td class="px-3 lg:px-6 py-4 whitespace-nowrap text-sm text-gray-500 hidden sm:table-cell">
                    ${store.purchase_count}
                </td>
                <td class="px-3 lg:px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div class="flex items-center">
                        <div class="w-12 lg:w-16 bg-gray-200 rounded-full h-2 mr-2">
                            <div class="bg-green-600 h-2 rounded-full" style="width: ${store.percentage}%"></div>
                        </div>
                        <span class="text-xs lg:text-sm">${store.percentage}%</span>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
        
        // Update pagination info
        this.updateTablePagination('store', store_analysis.length);
    }
    
    updateTablePagination(tableType, totalItems) {
        const pagination = this.tablePagination[tableType];
        const paginationDiv = document.getElementById(`${tableType}-table-pagination`);
        
        if (pagination.showAll || totalItems <= pagination.itemsPerPage) {
            paginationDiv.classList.add('hidden');
            return;
        }
        
        paginationDiv.classList.remove('hidden');
        
        // Update pagination info
        const startItem = (pagination.currentPage - 1) * pagination.itemsPerPage + 1;
        const endItem = Math.min(pagination.currentPage * pagination.itemsPerPage, totalItems);
        
        document.getElementById(`${tableType}-showing-start`).textContent = startItem;
        document.getElementById(`${tableType}-showing-end`).textContent = endItem;
        document.getElementById(`${tableType}-total`).textContent = totalItems;
        
        // Update button states
        const prevBtn = document.getElementById(`${tableType}-prev`);
        const nextBtn = document.getElementById(`${tableType}-next`);
        
        prevBtn.disabled = pagination.currentPage === 1;
        nextBtn.disabled = pagination.currentPage * pagination.itemsPerPage >= totalItems;
        
        // Add event listeners if not already added
        if (!prevBtn.hasAttribute('data-listener-added')) {
            prevBtn.addEventListener('click', () => {
                if (pagination.currentPage > 1) {
                    pagination.currentPage--;
                    this.updateDataTables();
                }
            });
            prevBtn.setAttribute('data-listener-added', 'true');
        }
        
        if (!nextBtn.hasAttribute('data-listener-added')) {
            nextBtn.addEventListener('click', () => {
                if (pagination.currentPage * pagination.itemsPerPage < totalItems) {
                    pagination.currentPage++;
                    this.updateDataTables();
                }
            });
            nextBtn.setAttribute('data-listener-added', 'true');
        }
    }
    
    toggleTableView(tableType) {
        const pagination = this.tablePagination[tableType];
        const button = document.getElementById(`${tableType}-table-toggle`);
        
        pagination.showAll = !pagination.showAll;
        pagination.currentPage = 1; // Reset to first page
        
        // Update button text
        if (pagination.showAll) {
            button.innerHTML = '<i class="fas fa-th-list mr-1"></i>Paginate';
        } else {
            button.innerHTML = '<i class="fas fa-list mr-1"></i>View All';
        }
        
        // Re-render table
        this.updateDataTables();
    }
    
    exportTableData(tableType) {
        if (!this.currentData) return;
        
        const data = tableType === 'category' 
            ? this.currentData.category_analysis.category_analysis
            : this.currentData.store_analysis.store_analysis;
        
        // Create CSV content
        let csvContent = '';
        
        if (tableType === 'category') {
            csvContent = 'Category,Spending,Items,Percentage\n';
            data.forEach(item => {
                csvContent += `"${item.category}","${item.total_spending}","${item.purchase_count}","${item.percentage}%"\n`;
            });
        } else {
            csvContent = 'Store,Spending,Items,Percentage\n';
            data.forEach(item => {
                csvContent += `"${item.store_name}","${item.total_spending}","${item.purchase_count}","${item.percentage}%"\n`;
            });
        }
        
        // Create and download file
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `${tableType}-analytics-${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    openFullscreenChart(chartId, title) {
        // Create modal if it doesn't exist
        let modal = document.getElementById('chart-fullscreen-modal');
        if (!modal) {
            modal = this.createFullscreenModal();
            document.body.appendChild(modal);
        }
        
        // Update modal title
        document.getElementById('modal-chart-title').textContent = title;
        
        // Show modal
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        
        // Clone the chart canvas
        const originalCanvas = document.getElementById(chartId);
        const modalCanvas = document.getElementById('modal-chart-canvas');
        
        // Copy canvas dimensions and context
        modalCanvas.width = originalCanvas.width;
        modalCanvas.height = originalCanvas.height;
        
        // Destroy existing modal chart
        if (this.charts.modalChart) {
            this.charts.modalChart.destroy();
        }
        
        // Create new chart in modal with same data
        const chartKey = this.getChartKey(chartId);
        const originalChart = this.charts[chartKey];
        
        if (originalChart) {
            this.charts.modalChart = new Chart(modalCanvas.getContext('2d'), {
                type: originalChart.config.type,
                data: JSON.parse(JSON.stringify(originalChart.data)),
                options: {
                    ...originalChart.options,
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        ...originalChart.options.plugins,
                        legend: {
                            ...originalChart.options.plugins?.legend,
                            display: true,
                            position: 'top'
                        }
                    }
                }
            });
        }
    }
    
    createFullscreenModal() {
        const modal = document.createElement('div');
        modal.id = 'chart-fullscreen-modal';
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 z-50 hidden flex items-center justify-center p-4';
        
        modal.innerHTML = `
            <div class="bg-white rounded-lg shadow-xl w-full max-w-6xl h-full max-h-[90vh] flex flex-col">
                <div class="flex justify-between items-center p-6 border-b">
                    <h2 id="modal-chart-title" class="text-2xl font-bold text-gray-800"></h2>
                    <div class="flex items-center space-x-2">
                        <button id="modal-export-btn" class="text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded px-3 py-1 transition-colors">
                            <i class="fas fa-download mr-1"></i>Export
                        </button>
                        <button id="modal-close-btn" class="text-gray-400 hover:text-gray-600 transition-colors">
                            <i class="fas fa-times text-xl"></i>
                        </button>
                    </div>
                </div>
                <div class="flex-1 p-6">
                    <div class="relative h-full">
                        <canvas id="modal-chart-canvas"></canvas>
                    </div>
                </div>
            </div>
        `;
        
        // Add event listeners
        modal.querySelector('#modal-close-btn').addEventListener('click', () => {
            this.closeFullscreenChart();
        });
        
        modal.querySelector('#modal-export-btn').addEventListener('click', () => {
            this.exportChart();
        });
        
        // Close on backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeFullscreenChart();
            }
        });
        
        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
                this.closeFullscreenChart();
            }
        });
        
        return modal;
    }
    
    closeFullscreenChart() {
        const modal = document.getElementById('chart-fullscreen-modal');
        if (modal) {
            modal.classList.add('hidden');
            document.body.style.overflow = '';
            
            // Destroy modal chart
            if (this.charts.modalChart) {
                this.charts.modalChart.destroy();
                delete this.charts.modalChart;
            }
        }
    }
    
    exportChart() {
        if (this.charts.modalChart) {
            const canvas = document.getElementById('modal-chart-canvas');
            const link = document.createElement('a');
            link.download = `${document.getElementById('modal-chart-title').textContent.toLowerCase().replace(/\s+/g, '-')}-chart.png`;
            link.href = canvas.toDataURL();
            link.click();
        }
    }
    
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount || 0);
    }
    
    // Responsive chart handling
    handleResize() {
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.resize === 'function') {
                chart.resize();
            }
        });
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.analyticsDashboard = new AnalyticsDashboard();
    
    // Handle window resize for responsive charts
    window.addEventListener('resize', () => {
        if (window.analyticsDashboard) {
            window.analyticsDashboard.handleResize();
        }
    });
});

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AnalyticsDashboard;
}