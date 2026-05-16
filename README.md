# Ballsdex-leaderboard-pack-v3
This is my first package for ballsdex v3, so its pretty small. Its pretty handy tho :3
## Installation
1. Put this into `config/extra.toml`
   ```toml
   [[ballsdex.packages]]
   location = "git+https://github.com/cewlgruyere/Leaderboard-BD.git"
   path = "leaderboard"
   enabled = true
   ```
2. Rebuild the bot.
   do:  
   ```
   docker compose build
   docker compose up
   ```
## Commands
*   **/Leaderboard** - Gives the top 10 players with the most balls in your dex! useful? not really. Adding more parameters soon.  
*   **Economy Argument** - Gives the top 10 players with the highest amount of currency, if enabled.  
*   **Amount Argument** - Gives the top n players, without a limit (it's intentional trust)  
*   **Ball Argument** - Gives the top 10 players that own a specific ball.
*   **Ephemeral Argument** - Boolean where you can choose if the message should be ephemeral or not.
