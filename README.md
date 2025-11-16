# 🌟 Virtual Trial Room - Next-Gen AI Fashion Platform

A stunning, premium virtual try-on application with 360° rotation capability, powered by Google's Gemini AI. Features an ultra-modern, futuristic UI design inspired by Nike and Apple's premium aesthetics.

## ✨ Features

- **Quick Try-On**: Instant virtual clothing try-on with AI
- **360° Rotation View**: See your outfit from all angles (8 different views)
- **Premium UI**: Sleek, futuristic design with glassmorphism effects
- **Drag & Drop Upload**: Easy image uploading with drag-and-drop support
- **Interactive Viewer**: Click through different angles or use auto-rotate
- **AI Stylist**: Built-in AI assistant for fashion recommendations
- **Responsive Design**: Works beautifully on all devices

## 🎨 Design Features

- **Theme**: Futuristic fashion + minimal luxury aesthetic
- **Colors**: Deep black, charcoal gray, electric blue, white accents
- **Effects**: 3D animations, glassmorphism, parallax scrolling, hover effects
- **Typography**: Clean, modern fonts (Poppins)
- **Layout**: High-end, immersive, professional-grade interface

## 📋 Prerequisites

- Python 3.8 or higher
- Google Gemini API Key
- Modern web browser

## 🚀 Installation

1. **Clone or download the project files**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up your environment variables**:
Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

To get a Gemini API key:
- Visit https://makersuite.google.com/app/apikey
- Sign in with your Google account
- Create a new API key
- Copy and paste it into your .env file

## 🎯 Usage

1. **Start the application**:
```bash
python app.py
```

2. **Open your browser**:
Navigate to `http://localhost:5000`

3. **Try it out**:
   - **Quick Try-On Mode**:
     - Upload your photo
     - Upload a clothing image
     - Click "Generate Try-On"
     - View your result instantly
   
   - **360° Rotation Mode**:
     - Upload your photo
     - Upload a clothing image
     - Click "Generate 360° Views"
     - Wait 3-5 minutes for all 8 angles to generate
     - Use the interactive viewer to explore all angles
     - Click "Auto-Rotate" to see an automatic rotation

## 📁 Project Structure

```
virtual-trial-room/
├── app.py                 # Main Flask application (backend)
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── css/
│   │   └── styles.css    # Premium UI styles
│   └── js/
│       └── main.js       # Interactive functionality
└── README.md             # This file
```

## 🎨 UI Sections

1. **Hero Section**: Full-screen intro with 3D model showcase
2. **Navigation**: Floating transparent nav bar with smooth scrolling
3. **Try-On Studio**: Dual-mode interface (Quick & 360°)
4. **Upload Area**: Drag-and-drop with preview
5. **Virtual Mirror**: Split-screen result display
6. **360° Viewer**: Interactive angle controls with auto-rotate
7. **AI Assistant**: Floating chatbot for recommendations
8. **Footer**: Clean layout with social links

## 🔧 Technical Details

- **Backend**: Flask (Python)
- **AI Model**: Google Gemini 2.0 Flash
- **Frontend**: Pure HTML, CSS, JavaScript (no frameworks)
- **Styling**: Custom CSS with glassmorphism and 3D effects
- **Image Processing**: PIL (Pillow)
- **API Communication**: Fetch API with async/await

## ⚡ Performance Notes

- **Quick Try-On**: ~10-30 seconds
- **360° Rotation**: ~3-5 minutes (generates 8 views)
- **Best Results**: Use clear, well-lit photos
- **Image Format**: Supports JPG, PNG, WEBP

## 🎯 Best Practices

1. **Photo Quality**: Use high-resolution images for best results
2. **Lighting**: Ensure photos are well-lit and clear
3. **Background**: Simple backgrounds work best
4. **Pose**: Front-facing poses produce better results
5. **Clothing**: Clear, visible clothing items work best

## 🐛 Troubleshooting

**Issue**: API Key Error
- **Solution**: Ensure your .env file contains a valid GEMINI_API_KEY

**Issue**: Images not uploading
- **Solution**: Check file format (must be image/jpeg, image/png, etc.)

**Issue**: 360° generation fails
- **Solution**: This generates 8 images and may take time. Ensure stable internet connection

**Issue**: Slow generation
- **Solution**: Normal for 360° mode. Quick mode is faster if you need instant results

## 🌐 Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge
- Opera

## 📱 Mobile Support

The UI is fully responsive and works on:
- Desktop (1920px+)
- Laptop (1366px)
- Tablet (768px)
- Mobile (375px+)

## 🎨 Customization

You can customize the theme by editing `static/css/styles.css`:
- Change colors in the `:root` variables
- Modify gradients for different effects
- Adjust animation timings
- Update typography

## 🔒 Privacy & Security

- Images are processed server-side
- Temporary files are automatically cleaned up
- No images are stored permanently
- API keys are kept in environment variables

## 📄 License

This project is provided as-is for educational and demonstration purposes.

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the Google Gemini API documentation
3. Ensure all dependencies are installed correctly

## 🎉 Hackathon Ready

This project is designed to impress hackathon judges with:
- Professional-grade UI/UX
- Cutting-edge AI technology
- Smooth, immersive experience
- Innovative 360° rotation feature
- Clean, maintainable code

---

**Built with ❤️ using Flask, Google Gemini AI, and modern web technologies**

*Experience Fashion. Virtually Real.*
