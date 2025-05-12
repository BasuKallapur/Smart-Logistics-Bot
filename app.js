// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyAcVZ3TKMvwoXtkmlp4MV9iWKqHCwAvBQc",
    authDomain: "log-bot-df281.firebaseapp.com",
    databaseURL: "https://log-bot-df281-default-rtdb.asia-southeast1.firebasedatabase.app",
    projectId: "log-bot-df281",
    storageBucket: "log-bot-df281.appspot.com",
    messagingSenderId: "774467457759",
    appId: "1:774467457759:web:b7cbc834450bb15c3f4f6a",
    measurementId: "G-2W4CZEWGLP"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const database = firebase.database();

// References to HTML elements
const currentLocationElem = document.getElementById('current-location');
const lastUpdateElem = document.getElementById('last-update');
const dispatchCountElem = document.getElementById('dispatch-count');
const damagedCountElem = document.getElementById('damaged-count');
const ewasteCountElem = document.getElementById('ewaste-count');
const rawCountElem = document.getElementById('raw-count');

// Location indicators
const locationIndicators = {
    'Start': document.getElementById('start-indicator'),
    'Building A': document.getElementById('a-indicator'),
    'Building B': document.getElementById('b-indicator'),
    'Building C': document.getElementById('c-indicator')
};

// Chart instances
let materialsChart;
let distributionChart;

// Initialize data
const materialData = {
    dispatchReady: 0,
    damaged: 0,
    eWaste: 0,
    rawMaterials: 0
};

// Function to format timestamps
function formatTimestamp(timestamp) {
    if (!timestamp) return '-';
    const date = new Date(timestamp);
    return date.toLocaleTimeString() + ', ' + date.toLocaleDateString();
}

// Function to update location display
function updateLocationDisplay(location) {
    currentLocationElem.textContent = location;
    
    // Reset all location styles
    document.getElementById('start-point').className = 'w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center relative';
    document.getElementById('building-a').className = 'w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center relative';
    document.getElementById('building-b').className = 'w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center relative';
    document.getElementById('building-c').className = 'w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center relative';
    
    // Highlight current location
    if (location === 'Start') {
        document.getElementById('start-point').className = 'w-16 h-16 rounded-full bg-green-200 border-2 border-green-500 flex items-center justify-center relative';
    } else if (location === 'Building A') {
        document.getElementById('building-a').className = 'w-16 h-16 rounded-full bg-green-200 border-2 border-green-500 flex items-center justify-center relative';
    } else if (location === 'Building B') {
        document.getElementById('building-b').className = 'w-16 h-16 rounded-full bg-green-200 border-2 border-green-500 flex items-center justify-center relative';
    } else if (location === 'Building C') {
        document.getElementById('building-c').className = 'w-16 h-16 rounded-full bg-green-200 border-2 border-green-500 flex items-center justify-center relative';
    }
    
    // Hide all indicators
    Object.values(locationIndicators).forEach(indicator => {
        if (indicator) indicator.classList.add('hidden');
    });
    
    // Show the current location indicator
    if (locationIndicators[location]) {
        locationIndicators[location].classList.remove('hidden');
    }
}

// Function to update material counts
function updateMaterialCounts(data) {
    materialData.dispatchReady = data.dispatchReady || 0;
    materialData.damaged = data.damaged || 0;
    materialData.eWaste = data.eWaste || 0;
    materialData.rawMaterials = data.rawMaterials || 0;
    
    dispatchCountElem.textContent = materialData.dispatchReady;
    damagedCountElem.textContent = materialData.damaged;
    ewasteCountElem.textContent = materialData.eWaste;
    rawCountElem.textContent = materialData.rawMaterials;
    
    updateCharts();
}

// Function to initialize charts
function initCharts() {
    // Materials History Chart (Bar chart)
    const materialsCtx = document.getElementById('materials-chart').getContext('2d');
    materialsChart = new Chart(materialsCtx, {
        type: 'bar',
        data: {
            labels: ['Dispatch Ready', 'Damaged Items', 'eWaste', 'Raw Materials'],
            datasets: [{
                label: 'Count',
                data: [
                    materialData.dispatchReady,
                    materialData.damaged,
                    materialData.eWaste,
                    materialData.rawMaterials
                ],
                backgroundColor: [
                    'rgba(72, 187, 120, 0.7)',
                    'rgba(237, 100, 100, 0.7)',
                    'rgba(159, 122, 234, 0.7)',
                    'rgba(66, 153, 225, 0.7)'
                ],
                borderColor: [
                    'rgb(72, 187, 120)',
                    'rgb(237, 100, 100)',
                    'rgb(159, 122, 234)',
                    'rgb(66, 153, 225)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            },
            responsive: true,
            maintainAspectRatio: false
        }
    });
    
    // Distribution Chart (Pie chart)
    const distributionCtx = document.getElementById('distribution-chart').getContext('2d');
    distributionChart = new Chart(distributionCtx, {
        type: 'pie',
        data: {
            labels: ['Dispatch Ready', 'Damaged Items', 'eWaste', 'Raw Materials'],
            datasets: [{
                data: [
                    materialData.dispatchReady,
                    materialData.damaged,
                    materialData.eWaste,
                    materialData.rawMaterials
                ],
                backgroundColor: [
                    'rgba(72, 187, 120, 0.7)',
                    'rgba(237, 100, 100, 0.7)',
                    'rgba(159, 122, 234, 0.7)',
                    'rgba(66, 153, 225, 0.7)'
                ],
                borderColor: [
                    'rgb(72, 187, 120)',
                    'rgb(237, 100, 100)',
                    'rgb(159, 122, 234)',
                    'rgb(66, 153, 225)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// Function to update charts
function updateCharts() {
    if (materialsChart && distributionChart) {
        // Update bar chart
        materialsChart.data.datasets[0].data = [
            materialData.dispatchReady,
            materialData.damaged,
            materialData.eWaste,
            materialData.rawMaterials
        ];
        materialsChart.update();
        
        // Update pie chart
        distributionChart.data.datasets[0].data = [
            materialData.dispatchReady,
            materialData.damaged,
            materialData.eWaste,
            materialData.rawMaterials
        ];
        distributionChart.update();
    }
}

// Initialize Firebase listeners
function initFirebaseListeners() {
    // Listen for location updates
    database.ref('currentLocation').on('value', (snapshot) => {
        const location = snapshot.val() || 'Start';
        updateLocationDisplay(location);
    });
    
    // Listen for timestamp updates
    database.ref('lastUpdate').on('value', (snapshot) => {
        lastUpdateElem.textContent = formatTimestamp(snapshot.val());
    });
    
    // Listen for material count updates
    database.ref('detectedMaterials').on('value', (snapshot) => {
        const data = snapshot.val() || {
            dispatchReady: 0,
            damaged: 0,
            eWaste: 0,
            rawMaterials: 0
        };
        updateMaterialCounts(data);
    });
}

// Setup test controls
function setupTestControls() {
    // Location buttons
    document.getElementById('loc-start').addEventListener('click', () => {
        database.ref('currentLocation').set('Start');
        database.ref('lastUpdate').set(firebase.database.ServerValue.TIMESTAMP);
    });
    
    document.getElementById('loc-a').addEventListener('click', () => {
        database.ref('currentLocation').set('Building A');
        database.ref('lastUpdate').set(firebase.database.ServerValue.TIMESTAMP);
    });
    
    document.getElementById('loc-b').addEventListener('click', () => {
        database.ref('currentLocation').set('Building B');
        database.ref('lastUpdate').set(firebase.database.ServerValue.TIMESTAMP);
    });
    
    document.getElementById('loc-c').addEventListener('click', () => {
        database.ref('currentLocation').set('Building C');
        database.ref('lastUpdate').set(firebase.database.ServerValue.TIMESTAMP);
    });
    
    // Materials update button
    document.getElementById('update-materials').addEventListener('click', () => {
        const dispatchValue = parseInt(document.getElementById('test-dispatch').value) || 0;
        const damagedValue = parseInt(document.getElementById('test-damaged').value) || 0;
        const ewasteValue = parseInt(document.getElementById('test-ewaste').value) || 0;
        const rawValue = parseInt(document.getElementById('test-raw').value) || 0;
        
        database.ref('detectedMaterials').set({
            dispatchReady: dispatchValue,
            damaged: damagedValue,
            eWaste: ewasteValue,
            rawMaterials: rawValue
        });
        
        database.ref('lastUpdate').set(firebase.database.ServerValue.TIMESTAMP);
    });
}

// Initialize Firebase data (for testing)
function initializeFirebaseData() {
    // Check if data exists first to avoid overwriting
    database.ref().once('value', (snapshot) => {
        const data = snapshot.val();
        if (!data) {
            // Set initial values if database is empty
            database.ref().set({
                currentLocation: 'Start',
                lastUpdate: firebase.database.ServerValue.TIMESTAMP,
                detectedMaterials: {
                    dispatchReady: 0,
                    damaged: 0,
                    eWaste: 0,
                    rawMaterials: 0
                }
            });
        }
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeFirebaseData();
    initCharts();
    initFirebaseListeners();
    setupTestControls();
    updateCurrentTime();
    
    // Update time every second
    setInterval(updateCurrentTime, 1000);
});

// Function to update current time display
function updateCurrentTime() {
    const timeElement = document.getElementById('current-time');
    if (timeElement) {
        const now = new Date();
        timeElement.textContent = now.toLocaleTimeString();
    }
} 