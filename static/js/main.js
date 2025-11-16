// ==========================================
// VIRTUAL TRIAL ROOM - ENHANCED JAVASCRIPT
// With Size Selection & Progressive Loading
// ==========================================

// Global Variables
let personImageFileCombined = null;
let clothingImageFileCombined = null;
let selectedSize = 'M';
let generatedResults = [];

// ==========================================
// INITIALIZATION
// ==========================================
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeFileUploads();
    initializeSizeSelector();
    initializeScrollAnimations();
});

// ==========================================
// NAVIGATION
// ==========================================
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            if (targetId.startsWith('#')) {
                const target = document.querySelector(targetId);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });
}

function scrollToTryon() {
    const tryonSection = document.getElementById('tryon');
    if (tryonSection) {
        tryonSection.scrollIntoView({ behavior: 'smooth' });
    }
}

// ==========================================
// SIZE SELECTOR
// ==========================================
function initializeSizeSelector() {
    const sizeButtons = document.querySelectorAll('.size-btn');
    
    sizeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            sizeButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            selectedSize = this.getAttribute('data-size');
            console.log('Selected size:', selectedSize);
        });
    });
}

// ==========================================
// FILE UPLOAD HANDLING
// ==========================================
function initializeFileUploads() {
    // Combined mode uploads
    setupUpload('person-image-combined', 'person-preview-combined', 'person-upload-combined', function(file) {
        personImageFileCombined = file;
        checkCombinedUploadComplete();
    });
    
    setupUpload('clothing-image-combined', 'clothing-preview-combined', 'clothing-upload-combined', function(file) {
        clothingImageFileCombined = file;
        checkCombinedUploadComplete();
    });
    
    // Generate button
    document.getElementById('combined-generate-btn').addEventListener('click', generateCombinedTryon);
}

function setupUpload(inputId, previewId, containerId, callback) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    const container = document.getElementById(containerId);
    const uploadLabel = container.querySelector('.upload-label');
    const previewContainer = container.querySelector('.preview-container');
    
    // Click upload
    input.addEventListener('change', function(e) {
        handleFileSelect(e.target.files[0], preview, uploadLabel, previewContainer, callback);
    });
    
    // Drag and drop
    container.addEventListener('dragover', function(e) {
        e.preventDefault();
        container.classList.add('drag-over');
    });
    
    container.addEventListener('dragleave', function(e) {
        e.preventDefault();
        container.classList.remove('drag-over');
    });
    
    container.addEventListener('drop', function(e) {
        e.preventDefault();
        container.classList.remove('drag-over');
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            handleFileSelect(file, preview, uploadLabel, previewContainer, callback);
        }
    });
}

function handleFileSelect(file, preview, uploadLabel, previewContainer, callback) {
    if (!file || !file.type.startsWith('image/')) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        preview.src = e.target.result;
        uploadLabel.style.display = 'none';
        previewContainer.style.display = 'block';
        callback(file);
    };
    reader.readAsDataURL(file);
}

function removeImageCombined(type) {
    if (type === 'person') {
        personImageFileCombined = null;
        document.getElementById('person-image-combined').value = '';
        document.querySelector('#person-upload-combined .upload-label').style.display = 'flex';
        document.querySelector('#person-upload-combined .preview-container').style.display = 'none';
    } else {
        clothingImageFileCombined = null;
        document.getElementById('clothing-image-combined').value = '';
        document.querySelector('#clothing-upload-combined .upload-label').style.display = 'flex';
        document.querySelector('#clothing-upload-combined .preview-container').style.display = 'none';
    }
    checkCombinedUploadComplete();
}

function checkCombinedUploadComplete() {
    const btn = document.getElementById('combined-generate-btn');
    btn.disabled = !(personImageFileCombined && clothingImageFileCombined);
}

// ==========================================
// COMBINED TRY-ON GENERATION WITH PROGRESSIVE LOADING
// ==========================================
async function generateCombinedTryon() {
    const btn = document.getElementById('combined-generate-btn');
    const btnContent = btn.querySelector('.btn-content');
    const btnLoader = btn.querySelector('.btn-loader');
    const placeholder = document.querySelector('.viewer-placeholder');
    const result = document.getElementById('combined-result');
    const statusPanel = document.getElementById('status-panel-combined');
    const statusContent = document.getElementById('status-content-combined');
    const progressiveGrid = document.getElementById('progressive-grid');
    
    // Reset
    generatedResults = [];
    progressiveGrid.innerHTML = '';
    document.getElementById('gif-container').style.display = 'none';
    
    // Show loading
    btnContent.style.display = 'none';
    btnLoader.style.display = 'flex';
    btn.disabled = true;
    
    placeholder.style.display = 'none';
    result.style.display = 'block';
    statusPanel.style.display = 'block';
    statusContent.textContent = 'Starting generation with size: ' + selectedSize + '\n';
    
    // Create placeholder items for all 8 views
    const labels = ['Front (2D)', '45° Right', 'Right Side', 'Back Right', 'Back', 'Back Left', 'Left Side', '45° Left'];
    labels.forEach((label, index) => {
        const item = document.createElement('div');
        item.className = 'progressive-item loading';
        item.id = `progressive-item-${index}`;
        item.innerHTML = `
            <div class="loading-placeholder">
                <i class="fas fa-spinner fa-spin" style="font-size: 2rem;"></i>
                <span>Waiting...</span>
            </div>
            <div class="item-label">${label}</div>
        `;
        progressiveGrid.appendChild(item);
    });
    
    try {
        // Prepare form data
        const formData = new FormData();
        formData.append('person_image', personImageFileCombined);
        formData.append('clothing_image', clothingImageFileCombined);
        formData.append('size', selectedSize);
        
        // Fetch with streaming
        const response = await fetch('/api/combined-tryon', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Failed to start generation');
        }
        
        // Read the stream
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n\n');
            buffer = lines.pop(); // Keep incomplete line in buffer
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.substring(6));
                        handleProgressiveUpdate(data);
                    } catch (e) {
                        console.error('Parse error:', e, line);
                    }
                }
            }
        }
        
        statusContent.textContent += '\n\n✓ Generation complete!';
        
    } catch (error) {
        console.error('Error:', error);
        statusContent.textContent += '\nError: ' + error.message;
        alert('Error: ' + error.message + '\n\nPlease check the console for details.');
    } finally {
        btnContent.style.display = 'flex';
        btnLoader.style.display = 'none';
        btn.disabled = false;
    }
}

function handleProgressiveUpdate(update) {
    const statusContent = document.getElementById('status-content-combined');
    
    console.log('Update received:', update.type);
    
    if (update.type === 'image') {
        // Update the progressive item
        const item = document.getElementById(`progressive-item-${update.data.index}`);
        if (item) {
            item.classList.remove('loading');
            item.innerHTML = `
                <img src="${update.data.image}" alt="${update.data.label}">
                <div class="item-label">${update.data.label}</div>
            `;
        }
        
        // Store result
        generatedResults.push(update.data);
        
        // Update status
        statusContent.textContent += `\n${update.message}`;
        statusContent.scrollTop = statusContent.scrollHeight;
        
    } else if (update.type === 'gif') {
        // Show GIF
        document.getElementById('gif-container').style.display = 'block';
        document.getElementById('result-gif').src = update.data;
        statusContent.textContent += `\n${update.message}`;
        
    } else if (update.type === 'error') {
        // Show error in item
        const item = document.getElementById(`progressive-item-${update.data.index}`);
        if (item) {
            item.classList.remove('loading');
            item.innerHTML = `
                <div class="loading-placeholder">
                    <i class="fas fa-exclamation-triangle" style="font-size: 2rem; color: #ff5722;"></i>
                    <span>Failed</span>
                </div>
                <div class="item-label">${update.data.label}</div>
            `;
        }
        statusContent.textContent += `\n${update.message}`;
        
    } else if (update.type === 'status') {
        statusContent.textContent += `\n${update.message}`;
        statusContent.scrollTop = statusContent.scrollHeight;
        
    } else if (update.type === 'complete') {
        statusContent.textContent += `\n\n${update.message}`;
        statusContent.scrollTop = statusContent.scrollHeight;
    }
}

function downloadAllResults() {
    if (generatedResults.length === 0) {
        alert('No results to download yet!');
        return;
    }
    
    generatedResults.forEach((result, index) => {
        setTimeout(() => {
            const link = document.createElement('a');
            link.href = result.image;
            link.download = `tryon-size-${selectedSize}-${result.label.replace(/[^a-z0-9]/gi, '-').toLowerCase()}.png`;
            link.click();
        }, index * 100); // Stagger downloads
    });
}

function resetCombined() {
    document.querySelector('.viewer-placeholder').style.display = 'flex';
    document.getElementById('combined-result').style.display = 'none';
    document.getElementById('status-panel-combined').style.display = 'none';
    generatedResults = [];
    
    // Reset size to M
    document.querySelectorAll('.size-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-size') === 'M') {
            btn.classList.add('active');
        }
    });
    selectedSize = 'M';
}

// ==========================================
// AI ASSISTANT
// ==========================================
function toggleAssistant() {
    const panel = document.querySelector('.assistant-panel');
    const isVisible = panel.style.display === 'block';
    panel.style.display = isVisible ? 'none' : 'block';
}

// ==========================================
// SCROLL ANIMATIONS
// ==========================================
function initializeScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.fade-in').forEach(el => {
        observer.observe(el);
    });
}

// Export functions for global access
window.scrollToTryon = scrollToTryon;
window.removeImageCombined = removeImageCombined;
window.downloadAllResults = downloadAllResults;
window.resetCombined = resetCombined;
window.toggleAssistant = toggleAssistant;
