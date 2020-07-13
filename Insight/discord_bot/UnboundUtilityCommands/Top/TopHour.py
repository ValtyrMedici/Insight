from .Top import Top
import discord


class TopHour(Top):
    async def get_embed(self, d_message: discord.Message, message_text: str, **kwargs) -> discord.Embed:
        return await self.get_top_embed(hour_range=1, d_message=d_message)

