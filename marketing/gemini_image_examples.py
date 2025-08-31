#!/usr/bin/env python3
"""
Example usage scripts for the Gemini Image Generator
"""

import os
from marketing.generate import GeminiImageGenerator


def example_basic_generation():
    """Example of basic image generation"""
    generator = GeminiImageGenerator()
    
    # Simple generation
    generator.generate_image(
        prompt="A serene Japanese garden with a wooden bridge over a koi pond, "
               "cherry blossoms in full bloom, soft morning light filtering through, "
               "photorealistic style with high detail",
        save_path="outputs/japanese_garden.png"
    )


def example_product_image():
    """Example of generating product images"""
    generator = GeminiImageGenerator()
    
    prompt = """
    Create a professional product photo of a luxury smartwatch:
    - Matte black titanium case with rose gold accents
    - Leather strap in deep brown color
    - Display showing 10:10 time with minimalist watch face
    - Placed on white marble surface
    - Soft studio lighting from the left
    - Shallow depth of field with blurred background
    - Ultra high resolution, commercial photography style
    """
    
    generator.generate_image(prompt, "outputs/luxury_watch.png")


def example_logo_design():
    """Example of generating a logo"""
    generator = GeminiImageGenerator()
    
    prompt = """
    Design a modern minimalist logo for "TechFlow":
    - Abstract geometric shape suggesting flow and technology
    - Use only two colors: deep blue (#1E3A8A) and electric cyan (#00D4FF)
    - Clean sans-serif typography for the company name
    - Should work on both light and dark backgrounds
    - Vector art style, flat design
    - Include the tagline "Innovation in Motion" below the logo
    """
    
    generator.generate_image(prompt, "outputs/techflow_logo.png")


def example_image_editing():
    """Example of editing an existing image"""
    generator = GeminiImageGenerator()
    
    # Assuming you have an input image
    generator.edit_image(
        image_path="inputs/original_photo.jpg",
        prompt="Remove the background and replace it with a gradient sunset sky. "
               "Add warm golden hour lighting to the subject. "
               "Enhance the colors to be more vibrant but natural.",
        save_path="outputs/edited_photo.png"
    )


def example_style_transfer():
    """Example of applying style to an image"""
    generator = GeminiImageGenerator()
    
    generator.edit_image(
        image_path="inputs/portrait.jpg",
        prompt="Transform this photo into a Van Gogh style oil painting. "
               "Use bold, expressive brushstrokes with swirling patterns. "
               "Apply a warm color palette with yellows and blues. "
               "Maintain the subject's features but with artistic interpretation.",
        save_path="outputs/portrait_vangogh.png"
    )


def example_image_composition():
    """Example of composing multiple images"""
    generator = GeminiImageGenerator()
    
    generator.compose_images(
        image_paths=[
            "inputs/landscape.jpg",
            "inputs/person.jpg",
            "inputs/objects.png"
        ],
        prompt="Create a surreal composition: "
               "Place the person from image 2 in the landscape from image 1. "
               "Integrate the objects from image 3 floating in the sky. "
               "Apply a dreamy, ethereal atmosphere with soft lighting. "
               "Ensure natural shadows and reflections for realism.",
        save_path="outputs/surreal_composition.png"
    )


def example_iterative_refinement():
    """Example of iteratively refining an image"""
    generator = GeminiImageGenerator()
    
    # First generation
    generator.generate_image(
        prompt="A futuristic cityscape at night with flying cars",
        save_path="outputs/city_v1.png"
    )
    
    # First refinement
    generator.refine_image(
        image_path="outputs/city_v1.png",
        refinement_prompt="Add more neon lights and holographic billboards. "
                         "Make the flying cars more prominent with light trails.",
        save_path="outputs/city_v2.png"
    )
    
    # Second refinement
    generator.refine_image(
        image_path="outputs/city_v2.png",
        refinement_prompt="Add rain effect with reflections on wet streets. "
                         "Include more atmospheric fog in the background.",
        save_path="outputs/city_final.png"
    )


def example_text_in_image():
    """Example of generating images with text"""
    generator = GeminiImageGenerator()
    
    prompt = """
    Create a motivational poster:
    - Dark gradient background from deep purple to black
    - Large bold text saying "DREAM BIG" in the center
    - Use modern, geometric sans-serif font
    - Add subtle glowing effect around the text
    - Include smaller text below: "The future belongs to those who believe"
    - Add abstract geometric shapes as decorative elements
    - Minimalist design with plenty of negative space
    """
    
    generator.generate_image(prompt, "outputs/motivational_poster.png")


def example_batch_variations():
    """Example of generating multiple variations"""
    generator = GeminiImageGenerator()
    
    base_prompt = "A cozy coffee shop interior with "
    variations = [
        "modern minimalist design, white walls, natural wood furniture",
        "vintage Victorian style, ornate decorations, velvet chairs",
        "industrial loft aesthetic, exposed brick, metal fixtures",
        "bohemian style, plants everywhere, colorful textiles"
    ]
    
    for i, variation in enumerate(variations, 1):
        generator.generate_image(
            prompt=base_prompt + variation,
            save_path=f"outputs/coffee_shop_v{i}.png"
        )


if __name__ == "__main__":
    try:
        # Create output directory
        os.makedirs("outputs", exist_ok=True)
        
        # The GeminiImageGenerator will automatically load credentials from:
        # 1. .credentials.json file (if exists)
        # 2. GEMINI_API_KEY environment variable
        
        # Run examples (uncomment the ones you want to test)
        print("Running basic generation example...")
        example_basic_generation()
        
        # example_product_image()
        # example_logo_design()
        # example_text_in_image()
        # example_batch_variations()
        
    except ValueError as e:
        print(f"Error: {e}")
        print("\nPlease ensure your API key is configured in .credentials.json")
        print("or set the GEMINI_API_KEY environment variable")