#!/usr/bin/env python3
"""
OpenAI GPT Image Generator with Cost Tracking
A Python script for creating and editing images using the OpenAI API
"""

import os
import sys
import json
import argparse
import hashlib
import asyncio
import aiohttp
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
import base64
from datetime import datetime
from decimal import Decimal
from PIL import Image
import io


def load_credentials():
    """Load API credentials from .credentials.json file"""
    creds_path = '.credentials.json'

    if Path(creds_path).exists():
        try:
            with open(creds_path, 'r') as f:
                creds = json.load(f)
                # Support both key names for flexibility
                return creds.get('OPENAI_API_KEY') or creds.get('openai_api_key')
        except Exception as e:
            print(f"Warning: Could not load credentials from {creds_path}: {e}")
    
    return None


class MetadataTracker:
    """Class to handle metadata and cost tracking for OpenAI"""
    
    # OpenAI DALL-E 3 pricing
    COST_PER_STANDARD_IMAGE = 0.040  # $0.040 per standard quality image
    COST_PER_HD_IMAGE = 0.080        # $0.080 per HD quality image
    
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
            "total_operations": 0
        }
    
    def calculate_cost(self, quality: str = "standard") -> float:
        """Calculate cost based on image quality"""
        if quality == "hd":
            return self.COST_PER_HD_IMAGE
        return self.COST_PER_STANDARD_IMAGE
    
    def save_generation_metadata(
        self, 
        operation: str,
        prompt: str,
        image_path: Optional[str],
        image_data: bytes,
        input_images: Optional[List[str]] = None,
        quality: str = "standard"
    ) -> Dict[str, Any]:
        """Save metadata for a generation operation"""
        
        # Create unique ID for this generation
        generation_id = hashlib.md5(
            f"{datetime.now().isoformat()}_{prompt[:50]}".encode()
        ).hexdigest()[:12]
        
        cost = self.calculate_cost(quality)
        
        # Create metadata record
        metadata = {
            "generation_id": generation_id,
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "prompt": prompt,
            "prompt_length": len(prompt),
            "output_image": str(image_path) if image_path else None,
            "input_images": input_images,
            "image_size_bytes": len(image_data),
            "quality": quality,
            "cost_usd": round(cost, 6),
            "model": "dall-e-3"
        }
        
        # Add to session data
        self.session_data["generations"].append(metadata)
        self.session_data["total_cost"] += cost
        self.session_data["total_operations"] += 1
        
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
                "total_operations": 0,
                "generation_count": 0
            }
        
        daily_data["generations"].append({
            "id": metadata["generation_id"],
            "time": metadata["timestamp"],
            "operation": metadata["operation"],
            "cost": metadata["cost_usd"]
        })
        daily_data["total_cost"] += metadata["cost_usd"]
        daily_data["total_operations"] = daily_data.get("total_operations", 0) + 1
        daily_data["generation_count"] += 1
        
        with open(daily_file, 'w') as f:
            json.dump(daily_data, f, indent=2)
    
    def get_session_summary(self) -> str:
        """Get summary of current session"""
        return (
            f"\n📊 Session Summary:\n"
            f"  • Operations: {len(self.session_data['generations'])}\n"
            f"  • Total operations: {self.session_data['total_operations']}\n"
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
            f"  • Operations: {data['generation_count']}\n"
            f"  • Total operations: {data['total_operations']}\n"
            f"  • Total cost: ${data['total_cost']:.4f}\n"
        )
    
    def get_all_time_stats(self) -> str:
        """Get all-time statistics"""
        total_cost = 0.0
        total_operations = 0
        total_generations = 0
        
        # Aggregate from all daily files
        for daily_file in self.daily_dir.glob("daily_*.json"):
            with open(daily_file, 'r') as f:
                data = json.load(f)
                total_cost += data.get("total_cost", 0)
                total_operations += data.get("total_operations", 0)
                total_generations += data.get("generation_count", 0)
        
        return (
            f"\n📊 All-Time Statistics:\n"
            f"  • Total generations: {total_generations}\n"
            f"  • Total operations: {total_operations}\n"
            f"  • Total cost: ${total_cost:.4f}\n"
            f"  • Average cost per generation: ${total_cost/max(total_generations, 1):.4f}\n"
        )


class GPTImageGenerator:
    """Class to handle image generation with OpenAI GPT API and cost tracking"""
    
    def __init__(self, api_key: Optional[str] = None, track_costs: bool = True):
        """
        Initialize the OpenAI client
        
        Args:
            api_key: OpenAI API key. If not provided, will look for:
                     1. .credentials.json file in script directory
                     2. OPENAI_API_KEY environment variable
            track_costs: Whether to track costs and save metadata
        """
        # Priority: passed key > credentials file > env var
        self.api_key = api_key or load_credentials() or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "API key required. Please either:\n"
                "1. Add your key to .credentials.json in the script directory\n"
                "2. Set OPENAI_API_KEY environment variable\n"
                "3. Pass api_key parameter"
            )
        
        self.base_url = "https://api.openai.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Initialize metadata tracker
        self.track_costs = track_costs
        if self.track_costs:
            self.tracker = MetadataTracker()
    
    async def generate_image(
        self, 
        prompt: str, 
        save_path: Optional[str] = None,
        quality: str = "standard",
        size: str = "1024x1024"
    ) -> Tuple[bytes, Dict]:
        """
        Generate an image from a text prompt
        
        Args:
            prompt: Text description of the image to generate
            save_path: Optional path to save the generated image
            quality: Image quality ("standard" or "hd")
            size: Image size ("1024x1024", "1792x1024", or "1024x1792")
            
        Returns:
            Tuple of (image data as bytes, metadata dict)
        """
        print(f"🎨 Generating image with prompt: {prompt[:100]}...")
        
        try:
            payload = {
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": size,
                "quality": quality,
                "response_format": "b64_json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/images/generations",
                    headers=self.headers,
                    json=payload
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        raise ValueError(f"API request failed: {response.status} - {error_text}")
                    
                    result = await response.json()
            
            # Extract image data
            if "data" in result and result["data"]:
                image_b64 = result["data"][0]["b64_json"]
                image_data = base64.b64decode(image_b64)
                
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
                        quality=quality
                    )
                    print(f"💰 Cost: ${metadata['cost_usd']:.4f}")
                
                return image_data, metadata
            
            raise ValueError("No image generated in response")
            
        except Exception as e:
            print(f"❌ Error generating image: {e}")
            raise
    
    async def refine_image(
        self, 
        image_path: str, 
        refinement_prompt: str, 
        save_path: Optional[str] = None,
        mask_path: Optional[str] = None,
        size: str = "1024x1024"
    ) -> Tuple[bytes, Dict]:
        """
        Edit an existing image using a text prompt
        
        Args:
            image_path: Path to the input image
            prompt: Text description of the edit to make
            save_path: Optional path to save the edited image
            mask_path: Optional path to mask image (PNG with transparency)
            size: Image size ("1024x1024", "1792x1024", or "1024x1792")
            
        Returns:
            Tuple of (edited image data as bytes, metadata dict)
        """
        print(f"✏️ Editing image: {image_path}")
        print(f"📝 Edit prompt: {refinement_prompt[:100]}...")
        
        try:
            # Calculate hash of original image for comparison
            with open(image_path, 'rb') as f:
                original_data = f.read()
            original_hash = hashlib.md5(original_data).hexdigest()
            print(f"🔍 DEBUG: Original image hash: {original_hash}")
            print(f"🔍 DEBUG: Original image size: {len(original_data)} bytes")
            
            # Convert image to RGBA format (required for OpenAI edits)
            image_rgba_data = self._convert_to_rgba(image_path)
            rgba_hash = hashlib.md5(image_rgba_data).hexdigest()
            print(f"🔍 DEBUG: RGBA converted image hash: {rgba_hash}")
            print(f"🔍 DEBUG: RGBA image size: {len(image_rgba_data)} bytes")
            
            mask_data = None
            if mask_path:
                with open(mask_path, 'rb') as f:
                    mask_data = f.read()
                print(f"🔍 DEBUG: Using mask: {mask_path}, size: {len(mask_data)} bytes")
            else:
                print(f"🔍 DEBUG: No mask provided")
            
            # Prepare form data
            data = aiohttp.FormData()
            data.add_field('image', image_rgba_data, filename=f"{Path(image_path).stem}_rgba.png", content_type='image/png')
            
            # Add mask if provided
            if mask_data:
                data.add_field('mask', mask_data, filename=Path(mask_path).name, content_type='image/png')
            
            # Add other parameters
            data.add_field('model', 'gpt-image-1')
            data.add_field('prompt', refinement_prompt)
            data.add_field('n', '1')
            data.add_field('size', size)
            
            print(f"🔍 DEBUG: Request parameters:")
            print(f"  - Model: gpt-image-1")
            print(f"  - Prompt: {refinement_prompt}")
            print(f"  - Size: {size}")
            print(f"  - Has mask: {mask_data is not None}")
            
            # Debug: Print all form fields being sent
            print(f"🔍 DEBUG: Form data fields:")
            try:
                for field in data._fields:
                    field_info = field[0]
                    field_name = field_info.get('name', 'unknown')
                    if field_name in ['image', 'mask']:
                        # For binary fields, try to get size
                        try:
                            field_value = field[2] if len(field) > 2 else field_info.get('value', b'')
                            size = len(field_value) if hasattr(field_value, '__len__') else 'unknown'
                            print(f"  - {field_name}: <binary data, {size} bytes>")
                        except:
                            print(f"  - {field_name}: <binary data>")
                    else:
                        field_value = field[2] if len(field) > 2 else field_info.get('value', 'unknown')
                        print(f"  - {field_name}: {field_value}")
            except Exception as debug_error:
                print(f"🔍 DEBUG: Error inspecting form data: {debug_error}")
                print(f"🔍 DEBUG: Form data structure: {type(data._fields)}")
                print(f"🔍 DEBUG: Number of fields: {len(data._fields)}")
            
            # Prepare headers (remove Content-Type to let aiohttp set it)
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            async with aiohttp.ClientSession() as session:
                print(f"🔍 DEBUG: Making request to {self.base_url}/images/edits")
                async with session.post(
                    f"{self.base_url}/images/edits",
                    headers=headers,
                    data=data
                ) as response:
                    
                    print(f"🔍 DEBUG: Response status: {response.status}")
                    print(f"🔍 DEBUG: Response headers: {dict(response.headers)}")
                    
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"🔍 DEBUG: Error response: {error_text}")
                        raise ValueError(f"API request failed: {response.status} - {error_text}")
                    
                    result = await response.json()
                    print(f"🔍 DEBUG: Response keys: {list(result.keys())}")
                    if "data" in result:
                        print(f"🔍 DEBUG: Number of images in response: {len(result['data'])}")
            
            # Extract edited image data
            if "data" in result and result["data"]:
                image_b64 = result["data"][0]["b64_json"]
                edited_data = base64.b64decode(image_b64)
                
                # Compare hashes to see if image actually changed
                edited_hash = hashlib.md5(edited_data).hexdigest()
                print(f"🔍 DEBUG: Edited image hash: {edited_hash}")
                print(f"🔍 DEBUG: Edited image size: {len(edited_data)} bytes")
                print(f"🔍 DEBUG: Images are identical: {original_hash == edited_hash}")
                
                # Additional debugging: check if RGBA conversion affected comparison
                print(f"🔍 DEBUG: RGBA vs original identical: {rgba_hash == original_hash}")
                print(f"🔍 DEBUG: RGBA vs edited identical: {rgba_hash == edited_hash}")
                
                if save_path:
                    await self._save_image(edited_data, save_path)
                
                # Track metadata and costs
                metadata = {}
                if self.track_costs:
                    metadata = self.tracker.save_generation_metadata(
                        operation="edit",
                        prompt=refinement_prompt,
                        image_path=save_path,
                        image_data=edited_data,
                        input_images=[image_path] + ([mask_path] if mask_path else [])
                    )
                    print(f"💰 Cost: ${metadata['cost_usd']:.4f}")
                
                return edited_data, metadata
            
            raise ValueError("No edited image in response")
            
        except Exception as e:
            print(f"❌ Error editing image: {e}")
            raise
    
    async def vary_image(
        self, 
        image_path: str, 
        save_path: Optional[str] = None,
        size: str = "1024x1024"
    ) -> Tuple[bytes, Dict]:
        """
        Create variations of an existing image
        
        Args:
            image_path: Path to the input image
            save_path: Optional path to save the variation
            size: Image size ("1024x1024", "1792x1024", or "1024x1792")
            
        Returns:
            Tuple of (variation image data as bytes, metadata dict)
        """
        print(f"🔄 Creating variation of: {image_path}")
        
        try:
            # Convert image to RGBA format (required for OpenAI variations)  
            image_rgba_data = self._convert_to_rgba(image_path)
            
            # Prepare form data
            data = aiohttp.FormData()
            data.add_field('image', image_rgba_data, filename=f"{Path(image_path).stem}_rgba.png", content_type='image/png')
            
            # Add other parameters
            data.add_field('n', '1')
            data.add_field('size', size)
            data.add_field('response_format', 'b64_json')
            
            # Prepare headers
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/images/variations",
                    headers=headers,
                    data=data
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        raise ValueError(f"API request failed: {response.status} - {error_text}")
                    
                    result = await response.json()
            
            # Extract variation data
            if "data" in result and result["data"]:
                image_b64 = result["data"][0]["b64_json"]
                variation_data = base64.b64decode(image_b64)
                
                if save_path:
                    await self._save_image(variation_data, save_path)
                
                # Track metadata and costs
                metadata = {}
                if self.track_costs:
                    metadata = self.tracker.save_generation_metadata(
                        operation="vary",
                        prompt=f"Variation of {Path(image_path).name}",
                        image_path=save_path,
                        image_data=variation_data,
                        input_images=[image_path]
                    )
                    print(f"💰 Cost: ${metadata['cost_usd']:.4f}")
                
                return variation_data, metadata
            
            raise ValueError("No variation generated in response")
            
        except Exception as e:
            print(f"❌ Error creating variation: {e}")
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
    
    def _get_content_type(self, file_path: str) -> str:
        """Get content type based on file extension"""
        ext = Path(file_path).suffix.lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp'
        }
        return content_types.get(ext, 'image/jpeg')
    
    def _convert_to_rgba(self, image_path: str) -> bytes:
        """Convert image to RGBA format required by OpenAI edit API"""
        with Image.open(image_path) as img:
            # Convert to RGBA if not already
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Save to bytes buffer as PNG
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            return buffer.getvalue()


def create_prompt_tips():
    """Print tips for creating effective prompts"""
    tips = """
    ========== PROMPT TIPS FOR BEST RESULTS ==========
    
    1. BE HYPER-SPECIFIC:
       ❌ "A cat"
       ✅ "A fluffy orange tabby cat sitting on a vintage wooden chair"
    
    2. PROVIDE CONTEXT AND INTENT:
       ❌ "Make it blue"
       ✅ "Change the sky color to deep azure blue for a twilight atmosphere"
    
    3. USE DETAILED DESCRIPTIONS:
       ✅ "A photorealistic portrait of a woman with curly red hair, 
           wearing a green dress, standing in a sunlit garden with roses"
    
    4. SPECIFY STYLE AND MOOD:
       ✅ "In the style of oil painting with impressionist brushstrokes"
       ✅ "Photorealistic with dramatic lighting and high contrast"
    
    5. FOR EDITS:
       ✅ "Add a rainbow in the sky above the mountains"
       ✅ "Change the person's shirt from blue to red"
    
    ==================================================
    """
    print(tips)


def show_cost_report(generator: GPTImageGenerator, args):
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
        description='Generate and edit images using OpenAI DALL-E API with cost tracking',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate a new image')
    gen_parser.add_argument('prompt', help='Text prompt for image generation')
    gen_parser.add_argument('-o', '--output', help='Output file path', 
                           default=f'generated_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
    gen_parser.add_argument('-q', '--quality', choices=['standard', 'hd'], default='standard',
                           help='Image quality')
    gen_parser.add_argument('-s', '--size', choices=['1024x1024', '1792x1024', '1024x1792'], 
                           default='1024x1024', help='Image size')
    
    # Edit command
    edit_parser = subparsers.add_parser('edit', help='Edit an existing image')
    edit_parser.add_argument('image', help='Path to input image')
    edit_parser.add_argument('prompt', help='Edit instructions')
    edit_parser.add_argument('-o', '--output', help='Output file path',
                            default=f'edited_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
    edit_parser.add_argument('-m', '--mask', help='Path to mask image (PNG with transparency)')
    edit_parser.add_argument('-s', '--size', choices=['1024x1024', '1792x1024', '1024x1792'], 
                           default='1024x1024', help='Image size')
    
    # Vary command
    vary_parser = subparsers.add_parser('vary', help='Create variations of an image')
    vary_parser.add_argument('image', help='Path to input image')
    vary_parser.add_argument('-o', '--output', help='Output file path',
                            default=f'variation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
    vary_parser.add_argument('-s', '--size', choices=['1024x1024', '1792x1024', '1024x1792'], 
                           default='1024x1024', help='Image size')
    
    # Cost report command
    report_parser = subparsers.add_parser('report', help='Show cost reports')
    report_parser.add_argument('report', choices=['session', 'daily', 'all'],
                              help='Type of report to show')
    report_parser.add_argument('--date', help='Date for daily report (YYYYMMDD format)')
    
    # Tips command
    tips_parser = subparsers.add_parser('tips', help='Show prompt writing tips')
    
    # Global options
    parser.add_argument('--api-key', help='OpenAI API key (or set OPENAI_API_KEY env var)')
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
        generator = GPTImageGenerator(
            api_key=args.api_key,
            track_costs=not args.no_tracking
        )
        
        # Execute command
        if args.command == 'generate':
            image_data, metadata = await generator.generate_image(
                args.prompt, 
                args.output,
                quality=args.quality,
                size=args.size
            )
            print(f"\n✅ Image generated successfully: {args.output}")
            if metadata:
                print(f"📊 Generation ID: {metadata['generation_id']}")
            
        elif args.command == 'edit':
            image_data, metadata = await generator.refine_image(
                args.image, 
                args.prompt, 
                args.output,
                mask_path=args.mask,
                size=args.size
            )
            print(f"\n✅ Image edited successfully: {args.output}")
            if metadata:
                print(f"📊 Generation ID: {metadata['generation_id']}")
            
        elif args.command == 'vary':
            image_data, metadata = await generator.vary_image(
                args.image, 
                args.output,
                size=args.size
            )
            print(f"\n✅ Image variation created successfully: {args.output}")
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