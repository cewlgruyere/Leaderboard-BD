import discord
from discord import app_commands, Embed, Color
from discord.ext import commands
from ballsdex.core.models import Player
from ballsdex.core.bot import BallsDexBot
from ballsdex.settings import settings
from tortoise.functions import Count
from ballsdex.core.utils.transformers import (
    BallEnabledTransform,
)



class component_view(discord.ui.LayoutView):
    def __init__(self, bot, interaction: discord.Interaction, players, amount: int, users, collectible):
        super().__init__(timeout=60)
        self.interaction = interaction
        self.players = players
        self.amount = amount
        self.bot = bot
        self.users = users
        self.page = 0
        self.pople_per_page = 5
        self.container = discord.ui.Container()
        self.economy = False
        
        if collectible:
            self.collectible = collectible
        else:
            self.collectible = None
        self.page_func()

    async def skp1(self, interaction: discord.Interaction):
        self.page = 0
        self.page_func()
        await interaction.response.edit_message(view=self)

    async def prv(self, interaction: discord.Interaction):
        if self.page > 0:
            self.page -= 1
        self.page_func()
        await interaction.response.edit_message(view=self)

    async def nxt(self, interaction: discord.Interaction):
        if self.page < self.max_pages() - 1:
            self.page += 1
        self.page_func()
        await interaction.response.edit_message(view=self)

    async def skpl(self, interaction: discord.Interaction):
        self.page = self.max_pages() - 1
        self.page_func()
        await interaction.response.edit_message(view=self)
    def max_pages(self):
        return max(1, (len(self.players) - 1) // self.pople_per_page + 1)

    def page_func(self):
        self.clear_items()

        s = self.page * self.pople_per_page
        e = s + self.pople_per_page
        if self.collectible:
            top_text = discord.ui.Section(
                discord.ui.TextDisplay(content=f"# {settings.bot_name} Leaderboard"),
                discord.ui.TextDisplay(content=f"Top {len(self.users)} players that own {self.collectible}(s)"),
                accessory=discord.ui.Thumbnail(
                    media=self.interaction.client.user.display_avatar.url,
                ),
            )
        else:
            top_text = discord.ui.Section(
                discord.ui.TextDisplay(content=f"# {settings.bot_name} Leaderboard"),
                discord.ui.TextDisplay(content=f"Top {len(self.users)} players"),
                accessory=discord.ui.Thumbnail(
                    media=self.interaction.client.user.display_avatar.url,
                ),
            )

        container = discord.ui.Container(
            top_text,
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.large)
        )


        
        for i, player in enumerate(self.players[s:e], start=s+1):
            user = self.users[i - 1]
            if self.collectible:
                leaderboard_player_text = discord.ui.Section(
                            discord.ui.TextDisplay(content=f"{i}. **{user.display_name}**\n{player.ball_count} {self.collectible}(s)"),
                            accessory=discord.ui.Thumbnail(
                                media=user.display_avatar.url,
                            ),
                        )
            else:
                leaderboard_player_text = discord.ui.Section(
                            discord.ui.TextDisplay(content=f"{i}. **{user.display_name}**\n{player.ball_count} {settings.plural_collectible_name}"),
                            accessory=discord.ui.Thumbnail(
                                media=user.display_avatar.url,
                            ),
                        )
            container.add_item(leaderboard_player_text)
        skp1 = discord.ui.Button(style=discord.ButtonStyle.secondary, label="<<", disabled=self.page == 0)
        prev = discord.ui.Button(style=discord.ButtonStyle.primary,   label="Previous", disabled=self.page == 0)
        nxt = discord.ui.Button(style=discord.ButtonStyle.primary,   label="Next", disabled=self.page >= self.max_pages() - 1)
        skpl = discord.ui.Button(style=discord.ButtonStyle.secondary, label=">>", disabled=self.page >= self.max_pages() - 1)

        skp1.callback = self.skp1
        prev.callback   = self.prv
        nxt.callback   = self.nxt
        skpl.callback  = self.skpl

        container.add_item(discord.ui.ActionRow(skp1, prev, nxt, skpl))
        self.add_item(container)
        self.add_item(discord.ui.TextDisplay(content="-# made by @unitedstatesoferland/cewlgruyere"))
    


class Leaderboard(commands.Cog):
    """
    Cog that adds a leaderboard command, to show who doesn't have maidens
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.checks.cooldown(1, 25, key=lambda i: i.user.id)
    @app_commands.command(name="leaderboard", description=f"Shows the top players of {settings.bot_name}!")
    async def leaderboard(self, interaction: discord.Interaction["BallsDexBot"], ephemeral: bool = False, amount: int = 10, collectible: BallEnabledTransform | None = None,):
        await interaction.response.defer(ephemeral=ephemeral, thinking=True)
        users = []
        if not collectible:
            players = await Player.all().annotate(
                ball_count=Count("balls")
            ).order_by("-ball_count").limit(amount)
        else:
            players = await Player.filter(
                balls__ball=collectible
            ).annotate(
                ball_count=Count("balls")
            ).order_by("-ball_count").limit(amount)

        if not players:
            await interaction.followup.send("No players found.", ephemeral=True)
            return

        for random_ass_var, player in enumerate(players, start=1):
            users.append(self.bot.get_user(player.discord_id) or await self.bot.fetch_user(player.discord_id))

        view = component_view(self.bot, interaction, players, amount, list(users), collectible)
        await interaction.followup.send(view=view)
