import discord
from discord.ext import commands
from discord import app_commands, Interaction, Embed
import requests

# ✅ Latest working localtunnel URL
OLLAMA_URL = "https://violet-carrots-burn.loca.lt"

class JengGPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="askjeng", description="Ask your local AI anything.")
    @app_commands.describe(prompt="What do you want to ask JengGPT?")
    async def askjeng(self, interaction: Interaction, prompt: str):
        await interaction.response.defer(thinking=True)

        try:
            print("🔁 Sending prompt to:", OLLAMA_URL)
            response = requests.post(f"{OLLAMA_URL}/api/generate", json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            })

            print("📡 Status Code:", response.status_code)
            print("🧾 Raw Response:", response.text[:300])

            data = response.json()
            answer = data.get("response", "No response received.")

            embed = Embed(
                title="🧠 JengGPT",
                description=answer.strip(),
                color=discord.Color.dark_teal()
            )
            embed.set_footer(text="Powered by Mistral via Ollama")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            print("❌ Exception occurred:", e)
            await interaction.followup.send(embed=Embed(
                title="❌ Error",
                description=f"```\n{str(e)}\n```",
                color=discord.Color.red()
            ))


async def setup(bot):
    await bot.add_cog(JengGPT(bot))
