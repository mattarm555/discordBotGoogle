import discord
from discord.ext import commands
from discord import app_commands, Interaction, Embed
import requests

# Replace with your live localtunnel URL:
OLLAMA_URL = "https://cold-peas-hang.loca.lt"

class JengGPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="askjeng", description="Ask your local AI anything.")
    @app_commands.describe(prompt="What do you want to ask JengGPT?")
    async def askjeng(self, interaction: Interaction, prompt: str):
        await interaction.response.defer(thinking=True)

        try:
            print("Sending prompt to:", OLLAMA_URL)
            response = requests.post(f"{OLLAMA_URL}/api/generate", json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            })

            print("Status Code:", response.status_code)
            print("Raw Response:", response.text[:300])  # Only show first 300 chars

            data = response.json()  # <-- this is what throws if response is empty or invalid
            answer = data.get("response", "No response received.")

            embed = Embed(
                title="🧠 JengGPT",
                description=answer.strip(),
                color=discord.Color.dark_teal()
            )
            embed.set_footer(text="powered by mistral via Ollama")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(embed=Embed(
                title="❌ Error",
                description=f"```\n{str(e)}\n```",
                color=discord.Color.red()
            ))


async def setup(bot):
    await bot.add_cog(JengGPT(bot))
