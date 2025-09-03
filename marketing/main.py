import os
from generate import GeminiImageGenerator
from generate_gpt import GPTImageGenerator
import uuid
import asyncio

semaphore = asyncio.Semaphore(4)

images = [
    {
        'name': 'invoice_sisyphus',
        'one': """The Invoice Sisyphus in a European Ligne Claire Tintin/Moebius style.

Playing on the Greek myth: Someone pushing a massive boulder made of crumpled invoices up a steep hill, only to have it roll back down (the eternal struggle of manual processing) in a European Ligne Claire Tintin/Moebius style.

The image must be very simple with a plain background so it can be easily understood at a glance. It must be almost symbolic in its simplicity.
""",
        'two': """make another version that is exactly the same except the person is wearing an engineer's hat, and directing two robots to perform the task for them. the robots are sleek and elegant and they have the task well under control. this should look like an edit of the first panel and will be used as a before/after comparison""",

    }
]


prompts = [
    "Minimalist illustration of frowning Sisyphus pushing enormous boulder made entirely of crumpled white invoices and receipts up steep hill, figure leaning hard into difficult task, unhappy expression visible, stark silhouette against empty sky ascending diagonal hillside, clean geometric composition, dramatic side lighting on inclined slope, monochromatic palette with paper texture, Greek pottery art style, ultra simple background",
    
    "Classical figure with grimacing face pushing giant spherical mass of compressed invoice papers up steep hillside, muscular form bent forward in laborious effort, frowning deeply, boulder of thousands of crumpled bills ascending incline, dramatic chiaroscuro lighting on hill slope, Renaissance painting style, empty void background, golden hour rim lighting, photorealistic rendering showing displeasure",
    
    "Stark vector art of frowning lone figure pushing massive paper boulder up sharp 45-degree hill, face showing clear frustration, boulder of wadded invoices rolling upward on steep grade, simplified human form exerting maximum effort uphill, flat design aesthetic, limited gray-white palette, negative space composition highlighting hill angle, vintage propaganda poster style, minimal environment",
    
    "Hyper-detailed oil painting, grimacing Sisyphus mid-push against colossal invoice sphere on severe hillside, unhappy expression clearly visible, documents spilling while rolling uphill, frowning face showing intense displeasure with task, Caravaggio-inspired dramatic lighting on slope, pitch black background, paper texture with readable headers, baroque intensity on inclined plane",
    
    "Clean line art of frowning figure pushing enormous invoice-paper boulder up steep hill gradient, frustrated facial expression in continuous line style, paper boulder ascending sharp incline, dynamic motion lines showing uphill effort, pen and ink aesthetic emphasizing hill angle, white background, Picasso-inspired minimalist sketch, pure symbolic upward movement with visible discontent",
    
    "Photorealistic 3D render, athletic figure with deeply furrowed brow pushing massive crumpled invoice sphere up dramatic hillside, unhappy expression in high detail, individual papers visible while rolling uphill, dramatic lighting from above on slope, volumetric atmosphere on incline, empty gradient background, 8K detail showing frustrated determination on hill",
    
    "Art deco poster, stylized frowning Sisyphus pushing geometric invoice boulder up triangular hill shape, downturned mouth visible, bold diagonal composition emphasizing upward slope, metallic gold on paper edges ascending hillside, black/white/gold palette, symmetrical hill design, 1920s commercial art, void background, elegant displeasure while climbing incline",
    
    "Expressionist painting, grimacing figure pushing chaotic invoice paper mass up steep hill, frowning face with visible frustration, brushstrokes showing uphill movement and difficulty, papers exploding/reforming while ascending slope, intense blue/white contrasts on hillside, empty void background, Francis Bacon-inspired dynamic upward motion, emotional discontent",
    
    "Japanese woodblock print, simplified frowning Sisyphus pushing round invoice boulder up stylized hill slope, downcast expression in minimal lines, origami-folded papers rolling uphill, wave patterns suggesting incline, limited palette with gradients showing elevation, ukiyo-e hill composition, empty sky, zen persistence despite visible unhappiness, wood grain texture",
    
    "Surrealist digital art, frowning figure pushing impossible invoice paper sphere up dreamlike hillside, frustrated expression clearly rendered, papers transforming while ascending magical slope, Magritte-inspired clarity on surreal incline, empty blue sky, photorealistic unhappy figure with supernatural paper physics rolling uphill, eternal dissatisfaction with upward task"
]

prompts = [
    "a simple logo which looks like two crossed keyboards (like crossed swords) 2 colors only, white on black background.",
    "a simple logo which looks like two crossed keyboards (like crossed swords) 2 colors only, white on black background.",
    "a simple logo which looks like two crossed keyboards (like crossed swords) 2 colors only, white on black background.",
    "a simple logo which looks like two crossed keyboards (like crossed swords) 2 colors only, white on black background.",
    "a simple logo which looks like two crossed keyboards (like crossed swords) 2 colors only, white on black background.",
    "a simple logo which looks like two crossed keyboards (like crossed swords) 2 colors only, white on black background.",
    "a simple logo which looks like two crossed keyboards (like crossed swords) 2 colors only, white on black background.",
    "a simple logo which looks like two crossed keyboards (like crossed swords) 2 colors only, white on black background.",

]

async def generate_single_first_stage(generator: GeminiImageGenerator, i, prompt, id):
    async with semaphore:
        await generator.generate_image(
            prompt=prompt,
            save_path=f"outputs/prompt_{i}-{id[:8]}.png",
            seed=i
        )

async def first_stage():
    id = str(uuid.uuid4())
    generator = GeminiImageGenerator()
    tasks = []
    for i, prompt in enumerate(prompts):
        task = generate_single_first_stage(generator, i, prompt, id)
        tasks.append(task)
    
    await asyncio.gather(*tasks)


async def generate_single_iteration(generator, i, id):
    async with semaphore:
        input_image = f"outputs/prompt_{i}-{id[:8]}.png"
        if os.path.exists(input_image):
            await generator.refine_image(
                image_path=input_image,
                refinement_prompt="create a version of this sisyphus image which looks like an edited version of the same image. The new image should look like an 'after' version of the first image which should look like a 'before' image. in the new image the sisyphus figure is enjoying himself, having a good time, relaxing. He is no longer pushing the boulder and he has found a way to automate the boulder rolling task using some kind of robot. the robot always looks sleek and in control.",
                save_path=f"outputs/prompt_{i}-{id[:8]}_automated.png"
            )

async def iterate():
    generator = GeminiImageGenerator()

    id = 'ff0faaa7'
    tasks = []
    for i in range(len(prompts)):
        task = generate_single_iteration(generator, i, id)
        tasks.append(task)
    
    await asyncio.gather(*tasks)


async def add_text():
    image = 'outputs/prompt_1-9783acad.png'
    generator = GPTImageGenerator()

    await generator.refine_image(
        image_path=image,
        refinement_prompt="add some more blank space around the boarder of the image and shrink the content a little. the blank borders must blend with the edges of the image.",
        save_path='sys_with_text.png'
    )
if __name__ == "__main__":
    # asyncio.run(add_text())
    asyncio.run(first_stage())
    # asyncio.run(iterate())

