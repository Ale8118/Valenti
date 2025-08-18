Super Valenti 2025

Super Valenti is a classic 2D platformer game developed with Python and the Pygame library. Guide Valenti, our hero, through a challenging world filled with platforms, enemies, and collectibles. The goal is to reach the end of each level, defeat all the enemies, and collect all the coins to become a true champion!

![spv](https://github.com/user-attachments/assets/fef02d95-9bc8-4644-be8f-826645ae436a)

Features
Classic Platformer Gameplay: Jump, run, and explore a hand-crafted level.

Player Abilities: Normal jump and a double jump to reach higher platforms and overcome obstacles.

Enemies: Watch out for moving enemies! You can defeat them by jumping on their heads.

Collectibles: Gather coins and special "beers" to boost your score and gain new abilities.

Dynamic Backgrounds: The background changes as you progress through the level, creating a more immersive experience.

Audio: Enjoy an original soundtrack and sound effects for jumps, collisions, and more.

Pause Menu: Take a break with an encouraging message and adjust the music and sound effects volume.
<img width="455" height="891" alt="Schermata 2025-08-18 alle 09 29 39" src="https://github.com/user-attachments/assets/31c3785d-b081-4ee2-b2a8-6978c489dd54" />

![spv2](https://github.com/user-attachments/assets/fb545ffa-8b97-4e5e-8eba-a67eb2f352dc)


Gameplay
The player controls Valenti, an agile hero who must navigate a series of platforms to reach the final goal.

Move: Use the left/right arrow keys or A/D to move.

Jump: Press the up arrow key, W, or Spacebar to jump. You can also perform a double jump after collecting a special item.

Defeat Enemies: Jump on the head of an enemy to defeat it and earn points.

Collect Items: Pick up coins and other items to increase your score.

Signs: Look for the signs to read special messages!

Pause: Press P to pause the game and access the volume controls.

![spv3](https://github.com/user-attachments/assets/0b2ee4cd-14f7-4e15-a0db-043b08cc7869)


How to Run
Prerequisites
You need to have Python and Pygame installed on your system.

Install Python: Download and install Python from the official website: python.org

![sp4](https://github.com/user-attachments/assets/6dbca498-8c82-45e8-b680-41f732ce7426)


Install Pygame: Open your terminal or command prompt and run the following command:

Bash

pip install pygame
Running the Game
Clone this repository to your local machine.

Make sure all the necessary assets (images and audio files) are in a subfolder named assets within the main game directory.

Open a terminal or command prompt, navigate to the game's folder, and run the following command:

Bash

python super_valenti.py
(Note: Replace super_valenti.py with the actual name of your Python file if it's different.)

Scoring
Coin: +5 points

Sign: +7 points

Enemy: +10 points

Beer: +2 points (and enables double jump!)

Your final score is calculated based on the total points you earn minus a penalty for the time taken to complete the level. The faster you are, the higher your score will be!

Code Structure
main.py (or the name of your file): Contains the Game class, which manages the main game loop, level generation, and all game logic.

Player class: Handles player movement, jumping, and collision detection.

Enemy class: Manages the behavior of enemies, including their movement and "dying" animation.

Collectible class: Represents items the player can collect.

Platform class: The base class for all solid platforms in the game.

Sign class: Displays encouraging or fun messages throughout the level.

River class: Creates a dynamically flowing river animation.

Backgrounds class: Manages the transitioning backgrounds.

assets folder: Contains all image (.png) and audio (.ogg) files.

![spv5](https://github.com/user-attachments/assets/ae14870f-21bd-4835-8a64-02969abcb78f)



