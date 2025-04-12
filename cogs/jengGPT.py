import discord
from discord.ext import commands
from discord import app_commands, Interaction, Embed
import requests
import base64
import os
from json.decoder import JSONDecodeError  # Add this import to catch JSON errors

OLLAMA_URL = "https://millennium-problems-building-bufing.trycloudflare.com"
SD_URL = "http://localhost:7860"
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
            }, timeout=20)

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

    @app_commands.command(name="draw", description="Generate an image from a text prompt.")
    @app_commands.describe(prompt="What do you want to see drawn?")
    async def draw(self, interaction: Interaction, prompt: str):
        await interaction.response.defer(thinking=True)

        try:
            print(f"🎨 Drawing prompt: {prompt}")
            response = requests.post(f"{SD_URL}/sdapi/v1/txt2img", json={
                "prompt": prompt,
                "steps": 25
            }, timeout=30)

            data = response.json()
            image_base64 = data['images'][0]

            # Decode and save the image
            image_bytes = base64.b64decode(image_base64.split(",", 1)[1])
            file_path = "generated_image.png"
            with open(file_path, "wb") as f:
                f.write(image_bytes)

            # Send it to Discord
            file = discord.File(file_path, filename="generated_image.png")
            await interaction.followup.send(
                content=f"🧠 Prompt: `{prompt}`",
                file=file
            )

            # Clean up
            os.remove(file_path)

        except Exception as e:
            print("❌ Image generation error:", e)
            await interaction.followup.send(embed=Embed(
                title="❌ Image Generation Failed",
                description=f"```\n{str(e)}\n```",
                color=discord.Color.red()
            ))

async def setup(bot):
    await bot.add_cog(JengGPT(bot))
