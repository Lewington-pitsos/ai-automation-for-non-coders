#!/usr/bin/env python3
"""
Google Imagen Image Generator with Cost Tracking
A Python script for creating images using the Google Imagen API
"""

import os
import sys
import json
import argparse
import hashlib
import asyncio
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from google import genai
from google.genai.types import (
    GenerateImageConfig,
    AspectRatio,
    SafetySetting,
    HarmCategory,
    HarmBlockThreshold,
    Image
)
from datetime import datetime


def load_credentials():
    """Load API credentials from .credentials.json file"""
    creds_path = '.credentials.json'

    if Path(creds_path).exists():
        try:
            with open(creds_path, 'r') as f:
                creds = json.load(f)
                # Support both key names for flexibility
                return creds.get('gemini_api_key') or creds.get('GOOGLE_GEMINI_API_KEY')
        except Exception as e:
            print(f"Warning: Could not load credentials from {creds_path}: {e}")
    
    return None


class MetadataTracker:
    """Class to handle metadata and cost tracking"""
    
    # Imagen 3 pricing: $0.04 per image for standard quality
    COST_PER_IMAGE = 0.04
    
    def __init__(self, metadata_dir: str = "metadata"):
        """Initialize metadata tracker"""
        self.script_dir = Path(__file__).parent
        self.metadata_dir = self.script_dir / metadata_dir
        self.metadata_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for organization
        self.daily_dir = self.metadata_dir / "daily"
        self.daily_dir.mkdir(exist_ok=True)
        
        self.sessions_dir = self.metadata_dir / "sessions"
        self.sessions_dir.mkdir(exist_ok=True)
        
        # Session ID for this run
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_file = self.sessions_dir / f"session_{self.session_id}.json"
        self.session_data = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "generations": [],
            "total_cost": 0.0,
            "total_images": 0
        }
    
    def calculate_cost(self, image_count: int = 1) -> float:
        """Calculate cost based on number of images"""
        return image_count * self.COST_PER_IMAGE
    
    def save_generation_metadata(
        self, 
        operation: str,
        prompt: str,
        image_path: Optional[str],
        image_data: bytes,
        config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Save metadata for a generation operation"""
        
        # Create unique ID for this generation
        generation_id = hashlib.md5(
            f"{datetime.now().isoformat()}_{prompt[:50]}".encode()
        ).hexdigest()[:12]
        
        cost = self.calculate_cost(1)
        
        # Create metadata record
        metadata = {
            "generation_id": generation_id,
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "prompt": prompt,
            "prompt_length": len(prompt),
            "output_image": str(image_path) if image_path else None,
            "image_size_bytes": len(image_data),
            "cost_usd": round(cost, 6),
            "model": "imagen-3.0-capability-001",
            "config": config
        }
        
        # Add to session data
        self.session_data["generations"].append(metadata)
        self.session_data["total_cost"] += cost
        self.session_data["total_images"] += 1
        
        # Save session file
        self._save_session_data()
        
        # Save daily summary
        self._update_daily_summary(metadata)
        
        # Save individual generation metadata
        gen_file = self.metadata_dir / f"gen_{generation_id}.json"
        with open(gen_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return metadata
    
    def _save_session_data(self):
        """Save current session data"""
        self.session_data["last_updated"] = datetime.now().isoformat()
        with open(self.session_file, 'w') as f:
            json.dump(self.session_data, f, indent=2)
    
    def _update_daily_summary(self, metadata: Dict):
        """Update daily summary file"""
        today = datetime.now().strftime("%Y%m%d")
        daily_file = self.daily_dir / f"daily_{today}.json"
        
        if daily_file.exists():
            with open(daily_file, 'r') as f:
                daily_data = json.load(f)
        else:
            daily_data = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "generations": [],
                "total_cost": 0.0,
                "total_images": 0,
                "generation_count": 0
            }
        
        daily_data["generations"].append({
            "id": metadata["generation_id"],
            "time": metadata["timestamp"],
            "operation": metadata["operation"],
            "cost": metadata["cost_usd"]
        })
        daily_data["total_cost"] += metadata["cost_usd"]
        daily_data["total_images"] += 1
        daily_data["generation_count"] += 1
        
        with open(daily_file, 'w') as f:
            json.dump(daily_data, f, indent=2)
    
    def get_session_summary(self) -> str:
        """Get summary of current session"""
        return (
            f"\n📊 Session Summary:\n"
            f"  • Generations: {len(self.session_data['generations'])}\n"
            f"  • Total images: {self.session_data['total_images']}\n"
            f"  • Total cost: ${self.session_data['total_cost']:.4f}\n"
        )
    
    def get_daily_summary(self, date: Optional[str] = None) -> str:
        """Get summary for a specific day"""
        if not date:
            date = datetime.now().strftime("%Y%m%d")
        
        daily_file = self.daily_dir / f"daily_{date}.json"
        if not daily_file.exists():
            return f"No data for date: {date}"
        
        with open(daily_file, 'r') as f:
            data = json.load(f)
        
        return (
            f"\n📊 Daily Summary for {data['date']}:\n"
            f"  • Generations: {data['generation_count']}\n"
            f"  • Total images: {data['total_images']}\n"
            f"  • Total cost: ${data['total_cost']:.4f}\n"
        )
    
    def get_all_time_stats(self) -> str:
        """Get all-time statistics"""
        total_cost = 0.0
        total_images = 0
        total_generations = 0
        
        # Aggregate from all daily files
        for daily_file in self.daily_dir.glob("daily_*.json"):
            with open(daily_file, 'r') as f:
                data = json.load(f)
                total_cost += data.get("total_cost", 0)
                total_images += data.get("total_images", 0)
                total_generations += data.get("generation_count", 0)
        
        return (
            f"\n📊 All-Time Statistics:\n"
            f"  • Total generations: {total_generations}\n"
            f"  • Total images: {total_images}\n"
            f"  • Total cost: ${total_cost:.4f}\n"
            f"  • Average cost per generation: ${total_cost/max(total_generations, 1):.4f}\n"
        )


class ImagenImageGenerator:
    """Class to handle image generation with Google Imagen API and cost tracking"""
    
    def __init__(self, api_key: Optional[str] = None, track_costs: bool = True):
        """
        Initialize the Imagen client
        
        Args:
            api_key: Google API key. If not provided, will look for:
                     1. .credentials.json file in script directory
                     2. GEMINI_API_KEY environment variable
            track_costs: Whether to track costs and save metadata
        """
        # Priority: passed key > credentials file > env var
        self.api_key = api_key or load_credentials() or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "API key required. Please either:\n"
                "1. Add your key to .credentials.json in the script directory\n"
                "2. Set GEMINI_API_KEY environment variable\n"
                "3. Pass api_key parameter"
            )
        
        self.client = genai.Client(api_key=self.api_key)
        self.model = "imagen-3.0-capability-001"
        
        # Initialize metadata tracker
        self.track_costs = track_costs
        if self.track_costs:
            self.tracker = MetadataTracker()
    
    async def generate_image(
        self, 
        prompt: str, 
        save_path: Optional[str] = None, 
        aspect_ratio: str = "1:1",
        safety_filter_level: str = "block_some"
    ) -> Tuple[bytes, Dict]:
        """
        Generate an image from a text prompt using Imagen 3
        
        Args:
            prompt: Text description of the image to generate
            save_path: Optional path to save the generated image
            aspect_ratio: Image aspect ratio (1:1, 3:4, 4:3, 9:16, 16:9)
            safety_filter_level: Safety filter level (block_most, block_some, block_few)
            
        Returns:
            Tuple of (image data as bytes, metadata dict)
        """
        print(f"🎨 Generating image with Imagen 3: {prompt[:100]}...")
        
        try:
            # Map aspect ratio strings to enum values
            aspect_ratio_map = {
                "1:1": AspectRatio.ASPECT_RATIO_1_1,
                "3:4": AspectRatio.ASPECT_RATIO_3_4,
                "4:3": AspectRatio.ASPECT_RATIO_4_3,
                "9:16": AspectRatio.ASPECT_RATIO_9_16,
                "16:9": AspectRatio.ASPECT_RATIO_16_9
            }
            
            # Map safety filter levels
            safety_map = {
                "block_most": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                "block_some": HarmBlockThreshold.BLOCK_ONLY_HIGH,
                "block_few": HarmBlockThreshold.BLOCK_NONE
            }
            
            # Configure generation settings
            config = GenerateImageConfig(
                number_of_images=1,
                aspect_ratio=aspect_ratio_map.get(aspect_ratio, AspectRatio.ASPECT_RATIO_1_1),
                safety_settings=[
                    SafetySetting(
                        category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                        threshold=safety_map.get(safety_filter_level, HarmBlockThreshold.BLOCK_ONLY_HIGH)
                    )
                ]
            )
            
            # Generate image using Imagen 3
            response = await asyncio.to_thread(
                self.client.models.generate_image,
                model=self.model,
                prompt=prompt,
                config=config
            )
            
            # Extract the generated image
            if response.generated_images and len(response.generated_images) > 0:
                generated_image = response.generated_images[0]
                
                # Convert PIL Image to bytes
                from io import BytesIO
                buffer = BytesIO()
                generated_image.image.save(buffer, format='PNG')
                image_data = buffer.getvalue()
                
                if save_path:
                    await self._save_image(image_data, save_path)
                
                # Track metadata and costs
                metadata = {}
                if self.track_costs:
                    metadata = self.tracker.save_generation_metadata(
                        operation="generate",
                        prompt=prompt,
                        image_path=save_path,
                        image_data=image_data,
                        config={
                            "aspect_ratio": aspect_ratio,
                            "safety_filter_level": safety_filter_level
                        }
                    )
                    print(f"💰 Cost: ${metadata['cost_usd']:.4f}")
                
                return image_data, metadata
            
            raise ValueError("No image generated in response")
            
        except Exception as e:
            print(f"❌ Error generating image: {e}")
            raise
    
    def get_session_stats(self) -> str:
        """Get current session statistics"""
        if self.track_costs and self.tracker:
            return self.tracker.get_session_summary()
        return "Cost tracking is disabled"
    
    def get_daily_stats(self, date: Optional[str] = None) -> str:
        """Get daily statistics"""
        if self.track_costs and self.tracker:
            return self.tracker.get_daily_summary(date)
        return "Cost tracking is disabled"
    
    def get_all_time_stats(self) -> str:
        """Get all-time statistics"""
        if self.track_costs and self.tracker:
            return self.tracker.get_all_time_stats()
        return "Cost tracking is disabled"
    
    async def _save_image(self, image_data: bytes, path: str):
        """Save image data to file"""
        try:
            # Ensure directory exists
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save the image
            with open(path, 'wb') as f:
                f.write(image_data)
            
            print(f"💾 Image saved to: {path}")
            
        except Exception as e:
            print(f"❌ Error saving image: {e}")
            raise


def create_prompt_tips():
    """Print tips for creating effective prompts"""
    tips = """
    ========== PROMPT TIPS FOR IMAGEN 3 ==========
    
    1. BE HYPER-SPECIFIC:
       ❌ "A cat"
       ✅ "A fluffy orange tabby cat sitting on a vintage wooden chair"
    
    2. DESCRIBE VISUAL DETAILS:
       ✅ "Photorealistic portrait with soft natural lighting"
       ✅ "Digital art style with vibrant colors and sharp details"
    
    3. SPECIFY COMPOSITION:
       ✅ "Close-up shot of subject with blurred background"
       ✅ "Wide landscape view with mountains in the distance"
    
    4. INCLUDE ATMOSPHERE AND MOOD:
       ✅ "Warm golden hour lighting with long shadows"
       ✅ "Dramatic storm clouds with contrasting bright foreground"
    
    5. FOR BEST QUALITY:
       ✅ Add "high quality, detailed, professional photography" to prompts
       ✅ Specify camera settings like "shot with Canon 5D, 85mm lens"
    
    ==============================================
    """
    print(tips)


def show_cost_report(generator: ImagenImageGenerator, args):
    """Show cost report based on arguments"""
    print("\n" + "="*50)
    print("💰 COST REPORT")
    print("="*50)
    
    if args.report == 'session':
        print(generator.get_session_stats())
    elif args.report == 'daily':
        print(generator.get_daily_stats(args.date))
    elif args.report == 'all':
        print(generator.get_all_time_stats())
    
    print("="*50)


async def main():
    """Main function to run the image generator"""
    parser = argparse.ArgumentParser(
        description='Generate images using Google Imagen 3 API with cost tracking',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate a new image')
    gen_parser.add_argument('prompt', help='Text prompt for image generation')
    gen_parser.add_argument('-o', '--output', help='Output file path', 
                           default=f'generated_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
    gen_parser.add_argument('-a', '--aspect-ratio', choices=['1:1', '3:4', '4:3', '9:16', '16:9'],
                           default='1:1', help='Image aspect ratio')
    gen_parser.add_argument('-s', '--safety', choices=['block_most', 'block_some', 'block_few'],
                           default='block_some', help='Safety filter level')
    
    # Cost report command
    report_parser = subparsers.add_parser('report', help='Show cost reports')
    report_parser.add_argument('report', choices=['session', 'daily', 'all'],
                              help='Type of report to show')
    report_parser.add_argument('--date', help='Date for daily report (YYYYMMDD format)')
    
    # Tips command
    tips_parser = subparsers.add_parser('tips', help='Show prompt writing tips')
    
    # Global options
    parser.add_argument('--api-key', help='Google API key (or set GEMINI_API_KEY env var)')
    parser.add_argument('--no-tracking', action='store_true', 
                       help='Disable cost tracking and metadata saving')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'tips':
        create_prompt_tips()
        return
    
    try:
        # Initialize generator
        generator = ImagenImageGenerator(
            api_key=args.api_key,
            track_costs=not args.no_tracking
        )
        
        # Execute command
        if args.command == 'generate':
            image_data, metadata = await generator.generate_image(
                args.prompt, 
                args.output,
                args.aspect_ratio,
                args.safety
            )
            print(f"\n✅ Image generated successfully: {args.output}")
            if metadata:
                print(f"📊 Generation ID: {metadata['generation_id']}")
            
        elif args.command == 'report':
            show_cost_report(generator, args)
            return
        
        # Show session summary after operations
        if not args.no_tracking and args.command != 'report':
            print(generator.get_session_stats())
    
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())