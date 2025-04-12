import discord
from discord.ext import commands
from discord import app_commands, Interaction, Embed
import requests
from json.decoder import JSONDecodeError

OLLAMA_URL = "https://breeding-lookup-performances-intro.trycloudflare.com"
DEFAULT_MODEL = "mistral"

# 🔍 Quick check to verify Ollama is up before deferring
def is_ollama_online() -> bool:
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=1)
        return response.status_code == 200
    except Exception:
        return False

class JengGPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="askjeng", description="Ask your local AI anything.")
    @app_commands.describe(
        prompt="What do you want to ask JengGPT?",
        model="Which model to use (e.g., mistral, llama2, codellama, llama2-uncensored)"
    )
    async def askjeng(self, interaction: Interaction, prompt: str, model: str = DEFAULT_MODEL):
        # 🔍 Check Ollama status BEFORE deferring
        if not is_ollama_online():
            if not interaction.response.is_done():
                await interaction.response.send_message(embed=Embed(
                    title="🛑 JengGPT is not available",
                    description="The AI backend (Ollama) is currently offline. Try again shortly.",
                    color=discord.Color.red()
                ), ephemeral=True)
            print("❌ Ollama server not available — skipping interaction.")
            return

        # 🛡️ Ensure we don't defer after already responding
        if interaction.response.is_done():
            print("⚠️ Interaction already acknowledged. Cannot defer.")
            return

        try:
            await interaction.response.defer(thinking=True)
        except (discord.NotFound, discord.HTTPException):
            print("❌ Could not defer. Interaction may have expired or already responded.")
            return

        try:
            print(f"📝 Prompt: {prompt}")
            print(f"🤖 Model selected: {model}")
            print("🔁 Sending prompt to:", OLLAMA_URL)

            response = requests.post(f"{OLLAMA_URL}/api/generate", json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }, timeout=15)

            print("📡 Status Code:", response.status_code)
            print("🧾 Raw Response:", response.text[:300])

            try:
                data = response.json()
            except JSONDecodeError:
                print("❌ Received non-JSON response from Ollama.")
                await interaction.followup.send(embed=Embed(
                    title="😴 JengGPT is Not Available",
                    description="Sorry, JengGPT is not here right now! Please try again later.",
                    color=discord.Color.orange()
                ))
                return

            answer = data.get("response", "No response received.")

            embed = Embed(
                title="🧠 JengGPT",
                description=f"**Prompt:** {prompt}\n\n{answer.strip()}",
                color=discord.Color.dark_teal()
            )
            embed.add_field(name="🤖 Model Used", value=model, inline=False)
            embed.set_footer(text=f"Powered by {model} via Ollama")

            await interaction.followup.send(embed=embed)

        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to Ollama server.")
            await interaction.followup.send(embed=Embed(
                title="😴 JengGPT is Offline",
                description="Sorry, JengGPT is not here right now! Please try again later.",
                color=discord.Color.orange()
            ))

        except requests.exceptions.Timeout:
            print("⏳ Request to Ollama timed out.")
            await interaction.followup.send(embed=Embed(
                title="⏳ Timeout",
                description="JengGPT took too long to respond. Try again in a moment!",
                color=discord.Color.orange()
            ))

        except Exception as e:
            print("❌ Exception occurred:", e)
            await interaction.followup.send(embed=Embed(
                title="❌ Error",
                description=f"```\n{str(e)}\n```",
                color=discord.Color.red()
            ))

async def setup(bot):
    await bot.add_cog(JengGPT(bot))
