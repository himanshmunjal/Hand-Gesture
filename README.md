# 🐍 Gesture-Controlled Snake Game

A modern implementation of the classic Snake game controlled by hand gestures using computer vision!

## ✨ Features

### Game Features
- **Classic Snake gameplay** with Nokia-inspired graphics
- **Gesture controls** - Move your hand to control the snake
- **Speed boost** - Pinch your thumb and index finger together
- **Power-ups** - Collect golden stars for bonus points
- **High score tracking** - Persistent high scores saved to file
- **Pause functionality** - Press SPACE to pause
- **Particle effects** - Visual feedback when eating fruit
- **Dual view** - See the game and camera feed side-by-side

### Technical Improvements
- ✅ **Fixed gesture detection** - Smooth, responsive controls
- ✅ **Thread-safe** - Proper locking for concurrent operations
- ✅ **Optimized performance** - 60 FPS gameplay
- ✅ **Gesture smoothing** - Reduced jitter and false detections
- ✅ **Better error handling** - Graceful degradation and recovery
- ✅ **Camera auto-detection** - Automatically finds available camera

## 📋 Requirements

```bash
pip install pygame opencv-python mediapipe numpy
```

### Required Python packages:
- `pygame` >= 2.0.0 - Game engine
- `opencv-python` >= 4.5.0 - Computer vision
- `mediapipe` >= 0.9.0 - Hand tracking
- `numpy` >= 1.20.0 - Numerical operations

## 🚀 Installation

1. **Clone or download** the game files:
   - `main.py`
   - `snake_game.py`
   - `gesture_control.py`

2. **Install dependencies**:
   ```bash
   pip install pygame opencv-python mediapipe numpy
   ```

3. **Run the game**:
   ```bash
   python main.py
   ```

## 🎮 How to Play

### Controls
- **Move hand UP** - Snake moves up
- **Move hand DOWN** - Snake moves down
- **Move hand LEFT** - Snake moves left
- **Move hand RIGHT** - Snake moves right
- **Pinch fingers** - Activate speed boost (thumb + index finger)
- **SPACE** - Pause game
- **ESC** - Quit game

### Gameplay
1. Position your hand in front of the camera
2. Move your hand in the direction you want the snake to go
3. Eat red fruits to grow and score points (10 points)
4. Collect golden stars for bonus points (20 points)
5. Avoid hitting walls or yourself
6. Show "UP" gesture when game over to restart

### Tips
- Keep your hand clearly visible to the camera
- Make deliberate movements - smooth is better than fast
- Use the speed boost strategically
- Watch for power-ups appearing after 30 points

## 🔧 Troubleshooting

### Camera Issues
**Problem**: Camera not detected
- **Solution**: Try different camera indices by modifying the code
- Check if other apps are using the camera
- Ensure camera permissions are granted

**Problem**: Laggy camera feed
- **Solution**: Reduce camera resolution in the code
- Close other resource-intensive applications

### Gesture Detection Issues
**Problem**: Gestures not recognized
- **Solution**: Ensure good lighting
- Keep hand at arm's length from camera
- Make sure entire hand is visible
- Avoid cluttered backgrounds

**Problem**: Snake moves erratically
- **Solution**: Move hand more slowly and deliberately
- Adjust `gesture_threshold` in `gesture_control.py`
- Ensure camera is stable and not moving

### Performance Issues
**Problem**: Low FPS or stuttering
- **Solution**: Reduce `target_fps` in main.py
- Lower camera resolution
- Update graphics drivers
- Close background applications

### Installation Issues
**Problem**: MediaPipe installation fails
- **Solution**: 
  ```bash
  pip install --upgrade pip
  pip install mediapipe --no-cache-dir
  ```

**Problem**: OpenCV errors
- **Solution**: Try different OpenCV version:
  ```bash
  pip install opencv-python==4.5.5.64
  ```

## 🎨 Customization

### Adjust Game Speed
In `snake_game.py`, modify:
```python
self.base_speed = 6  # Lower = slower, Higher = faster
self.boost_speed = 12  # Speed when boosting
```

### Change Gesture Sensitivity
In `gesture_control.py`, modify:
```python
self.gesture_threshold = 0.04  # Lower = more sensitive
```

### Adjust Grid Size
In `snake_game.py`:
```python
self.grid_size = 20  # Size of each grid cell in pixels
```

### Modify Colors
Colors are defined in `snake_game.py`:
```python
self.NOKIA_GREEN = (155, 188, 15)
self.RED = (255, 0, 0)
# Add your own!
```

## 📊 Game Mechanics

### Scoring
- **Fruit**: 10 points
- **Power-up**: 20 points
- **High score**: Automatically saved to `high_score.json`

### Difficulty
- Game maintains consistent speed
- Snake grows longer with each fruit
- More segments = harder to avoid yourself
- Power-ups spawn randomly after 30+ points

## 🐛 Known Issues

1. **Gesture lag**: There may be slight delay between hand movement and snake response due to gesture smoothing (this is intentional to reduce jitter)
2. **Camera flip**: If your camera feed appears backwards, this is normal (mirrored for intuitive control)
3. **Power-up spawn**: Occasionally power-ups may not spawn if there's insufficient space

## 🔮 Future Enhancements

Potential features to add:
- [ ] Multiple difficulty levels
- [ ] Obstacles and maze modes
- [ ] Two-player mode with two hands
- [ ] Custom gesture configurations
- [ ] Sound effects and music
- [ ] Different snake skins
- [ ] Leaderboard system
- [ ] Gesture training mode

## 📝 Code Structure

```
main.py              # Main game loop and window management
├── snake_game.py    # Game logic and rendering
└── gesture_control.py  # Hand tracking and gesture detection
```

### Key Classes
- `DualViewSnakeGame` - Main application controller
- `SnakeGame` - Game state and rendering
- `GestureControl` - Hand tracking and gesture recognition

## 💡 Development Notes

### Thread Safety
The application uses threading for concurrent gesture detection:
- Main thread: Game loop and rendering
- Background thread: Camera capture and gesture detection
- Lock protection: Shared state access

### Performance Optimizations
- Frame skipping for camera processing
- Gesture smoothing with position history
- Efficient particle system
- Optimized collision detection

## 🤝 Contributing

Feel free to fork and improve! Some areas that could use enhancement:
- Better gesture recognition algorithms
- More robust error handling
- Additional game modes
- Mobile device support

## 📄 License

This project is free to use and modify for personal and educational purposes.

## 🙏 Acknowledgments

- MediaPipe for hand tracking
- Pygame community
- Nokia for the original Snake inspiration

---

**Enjoy the game! 🎮🐍**

If you encounter any issues, check the troubleshooting section or modify the parameters to suit your setup.
