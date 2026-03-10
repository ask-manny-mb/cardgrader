// Global state
let uploadedImages = {
    front: null,
    back: null
};

// Image upload handler
function handleImageUpload(side, input) {
    const file = input.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
        showError('Please upload a valid image file.');
        return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
        showError('Image file size must be less than 10MB.');
        return;
    }

    const reader = new FileReader();
    reader.onload = function(e) {
        // Store the image data
        uploadedImages[side] = {
            data: e.target.result,
            file: file
        };

        // Update preview
        const preview = document.getElementById(`${side}-preview`);
        const placeholder = document.getElementById(`${side}-placeholder`);
        const image = document.getElementById(`${side}-image`);

        image.src = e.target.result;
        preview.classList.remove('hidden');
        placeholder.classList.add('hidden');

        // Update analyze button state
        updateAnalyzeButton();
    };

    reader.readAsDataURL(file);
}

// Clear image
function clearImage(side) {
    uploadedImages[side] = null;
    
    const preview = document.getElementById(`${side}-preview`);
    const placeholder = document.getElementById(`${side}-placeholder`);
    const input = document.getElementById(`${side}-upload`);

    preview.classList.add('hidden');
    placeholder.classList.remove('hidden');
    input.value = '';

    updateAnalyzeButton();
    hideError();
}

// Update analyze button state
function updateAnalyzeButton() {
    const analyzeBtn = document.getElementById('analyze-btn');
    const analyzeText = document.getElementById('analyze-text');
    
    if (uploadedImages.front && uploadedImages.back) {
        analyzeBtn.disabled = false;
        analyzeText.textContent = 'Analyze Card';
        analyzeBtn.classList.remove('bg-gray-300');
        analyzeBtn.classList.add('bg-primary', 'hover:bg-blue-700');
    } else {
        analyzeBtn.disabled = true;
        analyzeText.textContent = 'Upload both photos to analyze';
        analyzeBtn.classList.add('bg-gray-300');
        analyzeBtn.classList.remove('bg-primary', 'hover:bg-blue-700');
    }
}

// Analyze card function
async function analyzeCard() {
    if (!uploadedImages.front || !uploadedImages.back) {
        showError('Please upload both front and back photos of the card.');
        return;
    }

    // Show loading state
    const analyzeBtn = document.getElementById('analyze-btn');
    const analyzeText = document.getElementById('analyze-text');
    const analyzeLoading = document.getElementById('analyze-loading');
    
    analyzeBtn.disabled = true;
    analyzeText.classList.add('hidden');
    analyzeLoading.classList.remove('hidden');

    try {
        hideError();
        
        // Prepare form data
        const formData = new FormData();
        formData.append('front_image', uploadedImages.front.file);
        formData.append('back_image', uploadedImages.back.file);

        // Make API call
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `Server error: ${response.status}`);
        }

        const result = await response.json();
        
        // Display results
        displayResults(result);
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || 'Failed to analyze card. Please try again.');
    } finally {
        // Reset button state
        analyzeBtn.disabled = false;
        analyzeText.classList.remove('hidden');
        analyzeLoading.classList.add('hidden');
        updateAnalyzeButton();
    }
}

// Display results
function displayResults(result) {
    const resultsSection = document.getElementById('results-section');
    resultsSection.classList.remove('hidden');
    resultsSection.scrollIntoView({ behavior: 'smooth' });

    // Card Info
    displayCardInfo(result.card_info);
    
    // Grading Results
    displayGradingResults(result.grading);
    
    // Value Estimates
    displayValueEstimates(result.values);
    
    // Recommendation
    displayRecommendation(result.recommendation);
}

// Display card information
function displayCardInfo(cardInfo) {
    const cardInfoDiv = document.getElementById('card-info');
    
    const infoItems = [
        { label: 'Card Name', value: cardInfo.name },
        { label: 'Set', value: cardInfo.set },
        { label: 'Year', value: cardInfo.year },
        { label: 'Card Type', value: cardInfo.type },
        { label: 'Rarity', value: cardInfo.rarity }
    ].filter(item => item.value);

    cardInfoDiv.innerHTML = infoItems.map(item => 
        `<div class="flex justify-between">
            <span class="text-gray-600">${item.label}:</span>
            <span class="font-medium">${item.value}</span>
        </div>`
    ).join('');
}

// Display grading results
function displayGradingResults(grading) {
    const gradingDiv = document.getElementById('grading-results');
    
    const graders = ['PSA', 'CGC', 'TAG'];
    const criteria = ['centering', 'corners', 'edges', 'surface'];
    
    let html = '';
    
    // Overall grades
    html += '<div class="grid grid-cols-3 gap-4 mb-6">';
    graders.forEach(grader => {
        const grade = grading[grader.toLowerCase()];
        const gradeColor = getGradeColor(grade.overall);
        
        html += `
            <div class="text-center p-4 bg-gray-50 rounded-lg">
                <div class="text-sm text-gray-600 mb-1">${grader}</div>
                <div class="text-2xl font-bold text-${gradeColor}-600">${grade.overall}</div>
                <div class="text-xs text-gray-500">out of 10</div>
            </div>
        `;
    });
    html += '</div>';
    
    // Detailed breakdown
    html += '<div class="space-y-3">';
    criteria.forEach(criterion => {
        html += `
            <div class="bg-gray-50 rounded-lg p-3">
                <div class="flex justify-between items-center mb-2">
                    <span class="font-medium capitalize">${criterion}</span>
                    <span class="text-sm text-gray-600">${grading.psa[criterion]}/10</span>
                </div>
                <div class="text-sm text-gray-600">${grading.details[criterion]}</div>
            </div>
        `;
    });
    html += '</div>';
    
    gradingDiv.innerHTML = html;
}

// Display value estimates
function displayValueEstimates(values) {
    const valuesDiv = document.getElementById('value-estimates');
    
    let html = '';
    
    if (values.current_market) {
        html += `
            <div class="bg-blue-50 rounded-lg p-4">
                <h4 class="font-medium text-blue-900 mb-2">Current Market Value</h4>
                <div class="text-2xl font-bold text-blue-700">$${values.current_market.min} - $${values.current_market.max}</div>
                <div class="text-sm text-blue-600">Based on recent sales in similar condition</div>
            </div>
        `;
    }
    
    html += '<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">';
    ['PSA', 'CGC', 'TAG'].forEach(grader => {
        const value = values[grader.toLowerCase()];
        if (value) {
            html += `
                <div class="border rounded-lg p-3">
                    <div class="text-sm text-gray-600 mb-1">${grader} ${value.grade}</div>
                    <div class="font-bold text-lg">$${value.value}</div>
                    <div class="text-xs text-gray-500">Estimated value</div>
                </div>
            `;
        }
    });
    html += '</div>';
    
    valuesDiv.innerHTML = html;
}

// Display recommendation
function displayRecommendation(recommendation) {
    const recommendationDiv = document.getElementById('recommendation');
    
    const isWorthGrading = recommendation.worth_grading;
    const recommendationClass = isWorthGrading ? 'success' : 'warning';
    const recommendationIcon = isWorthGrading ? '✓' : '⚠';
    
    const html = `
        <div class="bg-${recommendationClass === 'success' ? 'green' : 'yellow'}-50 rounded-lg p-4 border border-${recommendationClass === 'success' ? 'green' : 'yellow'}-200">
            <div class="flex items-center mb-3">
                <span class="text-2xl mr-3">${recommendationIcon}</span>
                <h4 class="text-lg font-medium text-${recommendationClass === 'success' ? 'green' : 'yellow'}-900">
                    ${isWorthGrading ? 'Worth Grading!' : 'Consider Carefully'}
                </h4>
            </div>
            <p class="text-${recommendationClass === 'success' ? 'green' : 'yellow'}-800 mb-3">${recommendation.reason}</p>
            <div class="space-y-2 text-sm">
                <div><strong>Best Service:</strong> ${recommendation.best_service}</div>
                <div><strong>Estimated Cost:</strong> $${recommendation.estimated_cost}</div>
                <div><strong>Potential ROI:</strong> ${recommendation.potential_roi}</div>
            </div>
        </div>
    `;
    
    recommendationDiv.innerHTML = html;
}

// Helper functions
function getGradeColor(grade) {
    if (grade >= 9) return 'green';
    if (grade >= 7) return 'yellow';
    if (grade >= 5) return 'orange';
    return 'red';
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    
    errorText.textContent = message;
    errorDiv.classList.remove('hidden');
    errorDiv.scrollIntoView({ behavior: 'smooth' });
}

function hideError() {
    const errorDiv = document.getElementById('error-message');
    errorDiv.classList.add('hidden');
}

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    updateAnalyzeButton();
});