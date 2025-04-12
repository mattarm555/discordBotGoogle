import discord
from discord.ext import commands
from discord import app_commands, Interaction, Embed
import requests

OLLAMA_URL = "https://millennium-problems-building-bufing.trycloudflare.com"
DEFAULT_MODEL = "mistral"

class JengGPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="askjeng", description="Ask your local AI anything.")
    @app_commands.describe(
        prompt="What do you want to ask JengGPT?",
        model="Which model to use (e.g., mistral, llama2, codellama, llama2-uncensored)"
    )
    async def askjeng(self, interaction: Interaction, prompt: str, model: str = DEFAULT_MODEL):
        await interaction.response.defer(thinking=True)

        try:
            print(f"📝 Prompt: {prompt}")
            print(f"🤖 Model selected: {model}")
            print("🔁 Sending prompt to:", OLLAMA_URL)

            response = requests.post(f"{OLLAMA_URL}/api/generate", json={
                "model": model,
                "prompt": prompt,
                "stream": False
            })

            print("📡 Status Code:", response.status_code)
            print("🧾 Raw Response:", response.text[:300])

            data = response.json()
            answer = data.get("response", "No response received.")

            embed = Embed(
                title="🧠 JengGPT",
                description=f"**Prompt:** {prompt}\n\n{answer.strip()}",
                color=discord.Color.dark_teal()
            )
            embed.add_field(name="🤖 Model Used", value=model, inline=False)
            embed.set_footer(text=f"Powered by {model} via Ollama")
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
