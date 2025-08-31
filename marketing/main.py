from generate import GeminiImageGenerator
import uuid


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
    "Minimalist illustration of Sisyphus pushing enormous boulder made entirely of crumpled white invoices and receipts up steep mountain slope, figure leaning into task with determination, stark silhouette against empty sky, clean geometric composition, dramatic side lighting, monochromatic palette with hints of paper texture, inspired by Greek pottery art style, ultra simple background, no distractions",
    
    "Classical figure pushing giant spherical mass of compressed invoice papers uphill, muscular form bent forward in focused effort, boulder constructed from thousands of visible crumpled bills and statements, dramatic chiaroscuro lighting, Renaissance painting style, empty void background, golden hour rim lighting on paper edges, photorealistic rendering, heroic scale",
    
    "Stark vector art of lone figure pushing massive paper boulder up 45-degree incline, boulder clearly made of wadded invoices with visible numbers and text, simplified human form showing extreme effort, flat design aesthetic, limited color palette of grays and whites, negative space composition, inspired by vintage propaganda posters, absolutely minimal environment",
    
    "Hyper-detailed oil painting style, Sisyphus mid-push against colossal sphere of crumpled financial documents, invoices spilling and reforming into boulder shape, determined expression on figure, Caravaggio-inspired dramatic lighting, pitch black background, paper texture clearly visible with invoice headers readable, baroque intensity, isolated moment of effort",
    
    "Clean line art illustration, figure pushing enormous invoice-paper boulder up severe gradient, continuous line drawing style, paper boulder showing layers of compressed bills and receipts, dynamic motion lines indicating effort, pen and ink aesthetic, white background, inspired by Picasso's minimalist sketches, pure symbolic representation",
    
    "Photorealistic 3D render, athletic figure working to push massive sphere of realistically crumpled invoices upward, individual papers visible with barcodes and numbers, subsurface scattering on paper, dramatic single light source from above, volumetric atmosphere, empty gradient background, hyperrealistic detail showing focused determination, 8K detail",
    
    "Art deco style poster, stylized Sisyphus pushing geometric boulder of angular folded invoices up triangular mountain, bold shapes and strong diagonal composition, metallic gold accents on paper edges, limited palette of black, white, and gold, symmetrical design elements, inspired by 1920s commercial art, void background, elegant determination",
    
    "Expressionist painting style, figure pushing chaotic mass of invoice papers formed into boulder shape, visible brushstrokes showing movement and energy, papers seeming to explode and reform, intense contrasts, emotional color palette of deep blues and stark whites, empty background suggesting infinite void, inspired by Francis Bacon's dynamic figures",
    
    "Japanese woodblock print style, simplified Sisyphus pushing perfectly round boulder of origami-folded invoices up stylized slope, wave-like patterns in paper texture, limited color palette with subtle gradients, ukiyo-e inspired composition, empty sky with single gradient, meditative persistence, zen-like simplicity, visible wood grain texture",
    
    "Surrealist digital art, figure pushing impossible boulder of floating, swirling invoice papers that form sphere through motion, papers caught mid-transformation between flat documents and round boulder, dreamlike lighting, Magritte-inspired clarity, perfectly empty blue sky background, photorealistic figure with supernatural paper physics, eternal task"
]

def main():
    id = str(uuid.uuid4())
    generator = GeminiImageGenerator()
    for i, prompt in enumerate(prompts):
        generator.generate_image(
            prompt=prompt,
            save_path=f"outputs/prompt_{i}-{id[:8]}.png"
        )

def iterate():
    generator = GeminiImageGenerator()

    for i in range(10):
        for sequence in images:
            generator.generate_image(
                prompt=sequence['one'],
                save_path=f"outputs/{sequence['name']}-{i}.png"
            )
        
            generator.refine_image(
                image_path=f"outputs/{sequence['name']}-{i}.png",
                refinement_prompt=sequence['two'],
                save_path=f"outputs/{sequence['name']}-{i}_v2.png"
            )

if __name__ == "__main__":
    main()