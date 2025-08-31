#!/usr/bin/env python3
"""
Google Gemini Image Generator with Cost Tracking
A Python script for creating images using the Google Gemini API
"""

import os
import sys
import json
import argparse
import hashlib
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from google import genai
import base64
from datetime import datetime
from decimal import Decimal


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
    
    COST_PER_MILLION_TOKENS = 0.075  # $0.075 per 1M output tokens for Gemini 2.5 Flash
    
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
            "total_tokens": 0
        }
    
    def calculate_cost(self, token_count: int) -> float:
        """Calculate cost based on token count"""
        return (token_count / 1_000_000) * self.COST_PER_MILLION_TOKENS
    
    def estimate_tokens_from_image(self, image_data: bytes) -> int:
        """Estimate token count from image size (rough approximation)"""
        # Rough estimate: ~1 token per 4 bytes for image data
        # This is an approximation as actual token count varies
        return len(image_data) // 4
    
    def save_generation_metadata(
        self, 
        operation: str,
        prompt: str,
        image_path: Optional[str],
        image_data: bytes,
        input_images: Optional[List[str]] = None,
        usage_metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Save metadata for a generation operation"""
        
        # Create unique ID for this generation
        generation_id = hashlib.md5(
            f"{datetime.now().isoformat()}_{prompt[:50]}".encode()
        ).hexdigest()[:12]
        
        # Estimate or get actual token count
        if usage_metadata and 'total_token_count' in usage_metadata:
            token_count = usage_metadata['total_token_count']
        else:
            # Estimate from image size
            token_count = self.estimate_tokens_from_image(image_data)
        
        cost = self.calculate_cost(token_count)
        
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
            "estimated_tokens": token_count,
            "cost_usd": round(cost, 6),
            "model": "gemini-2.5-flash-image-preview"
        }
        
        # Add to session data
        self.session_data["generations"].append(metadata)
        self.session_data["total_cost"] += cost
        self.session_data["total_tokens"] += token_count
        
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
                "total_tokens": 0,
                "generation_count": 0
            }
        
        daily_data["generations"].append({
            "id": metadata["generation_id"],
            "time": metadata["timestamp"],
            "operation": metadata["operation"],
            "cost": metadata["cost_usd"]
        })
        daily_data["total_cost"] += metadata["cost_usd"]
        daily_data["total_tokens"] += metadata["estimated_tokens"]
        daily_data["generation_count"] += 1
        
        with open(daily_file, 'w') as f:
            json.dump(daily_data, f, indent=2)
    
    def get_session_summary(self) -> str:
        """Get summary of current session"""
        return (
            f"\n📊 Session Summary:\n"
            f"  • Generations: {len(self.session_data['generations'])}\n"
            f"  • Total tokens: {self.session_data['total_tokens']:,}\n"
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
            f"  • Total tokens: {data['total_tokens']:,}\n"
            f"  • Total cost: ${data['total_cost']:.4f}\n"
        )
    
    def get_all_time_stats(self) -> str:
        """Get all-time statistics"""
        total_cost = 0.0
        total_tokens = 0
        total_generations = 0
        
        # Aggregate from all daily files
        for daily_file in self.daily_dir.glob("daily_*.json"):
            with open(daily_file, 'r') as f:
                data = json.load(f)
                total_cost += data.get("total_cost", 0)
                total_tokens += data.get("total_tokens", 0)
                total_generations += data.get("generation_count", 0)
        
        return (
            f"\n📊 All-Time Statistics:\n"
            f"  • Total generations: {total_generations}\n"
            f"  • Total tokens used: {total_tokens:,}\n"
            f"  • Total cost: ${total_cost:.4f}\n"
            f"  • Average cost per generation: ${total_cost/max(total_generations, 1):.4f}\n"
        )


class GeminiImageGenerator:
    """Class to handle image generation with Google Gemini API and cost tracking"""
    
    def __init__(self, api_key: Optional[str] = None, track_costs: bool = True):
        """
        Initialize the Gemini client
        
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
        self.model = "gemini-2.5-flash-image-preview"
        
        # Initialize metadata tracker
        self.track_costs = track_costs
        if self.track_costs:
            self.tracker = MetadataTracker()
    
    def generate_image(self, prompt: str, save_path: Optional[str] = None) -> Tuple[bytes, Dict]:
        """
        Generate an image from a text prompt
        
        Args:
            prompt: Text description of the image to generate
            save_path: Optional path to save the generated image
            
        Returns:
            Tuple of (image data as bytes, metadata dict)
        """
        print(f"🎨 Generating image with prompt: {prompt[:100]}...")
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt]
            )
            
            # Extract usage metadata if available
            usage_metadata = None
            if hasattr(response, 'usage_metadata'):
                usage_metadata = response.usage_metadata
            
            # Check for prohibited content and handle gracefully
            if response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason') and str(candidate.finish_reason) == 'FinishReason.PROHIBITED_CONTENT':
                    print(f"⚠️ Warning: Content blocked due to safety policies. Skipping this generation.")
                    return b'', {}
                
                if candidate.content is None:
                    print(f"🔍 Debug: Content is None - finish reason: {getattr(candidate, 'finish_reason', 'unknown')}")
                    if hasattr(response, 'prompt_feedback'):
                        print(f"🔍 Debug: Prompt feedback: {response.prompt_feedback}")
                    print(f"⚠️ Warning: Generation failed or was blocked. Skipping this generation.")
                    return b'', {}
            
            # Extract image data from response
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        # The data is already in bytes format, not base64 encoded
                        image_data = part.inline_data.data if isinstance(part.inline_data.data, bytes) else base64.b64decode(part.inline_data.data)
                        
                        if save_path:
                            self._save_image(image_data, save_path)
                        
                        # Track metadata and costs
                        metadata = {}
                        if self.track_costs:
                            metadata = self.tracker.save_generation_metadata(
                                operation="generate",
                                prompt=prompt,
                                image_path=save_path,
                                image_data=image_data,
                                usage_metadata=usage_metadata
                            )
                            print(f"💰 Estimated cost: ${metadata['cost_usd']:.4f}")
                        
                        return image_data, metadata
            
            raise ValueError("No image generated in response")
            
        except Exception as e:
            print(f"❌ Error generating image: {e}")
            raise
    
    def edit_image(
        self, 
        image_path: str, 
        prompt: str, 
        save_path: Optional[str] = None
    ) -> Tuple[bytes, Dict]:
        """
        Edit an existing image using a text prompt
        
        Args:
            image_path: Path to the input image
            prompt: Text description of the edit to make
            save_path: Optional path to save the edited image
            
        Returns:
            Tuple of (edited image data as bytes, metadata dict)
        """
        print(f"✏️ Editing image: {image_path}")
        print(f"📝 Edit prompt: {prompt[:100]}...")
        
        try:
            # Load and encode the input image
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            
            # Create content with both image and text
            contents = [
                {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": self._get_mime_type(image_path),
                                "data": encoded_image
                            }
                        },
                        {"text": prompt}
                    ]
                }
            ]
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents
            )
            
            # Extract usage metadata if available
            usage_metadata = None
            if hasattr(response, 'usage_metadata'):
                usage_metadata = response.usage_metadata
            
            # Extract edited image from response
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        # The data is already in bytes format, not base64 encoded
                        edited_data = part.inline_data.data if isinstance(part.inline_data.data, bytes) else base64.b64decode(part.inline_data.data)
                        
                        if save_path:
                            self._save_image(edited_data, save_path)
                        
                        # Track metadata and costs
                        metadata = {}
                        if self.track_costs:
                            metadata = self.tracker.save_generation_metadata(
                                operation="edit",
                                prompt=prompt,
                                image_path=save_path,
                                image_data=edited_data,
                                input_images=[image_path],
                                usage_metadata=usage_metadata
                            )
                            print(f"💰 Estimated cost: ${metadata['cost_usd']:.4f}")
                        
                        return edited_data, metadata
            
            raise ValueError("No edited image in response")
            
        except Exception as e:
            print(f"❌ Error editing image: {e}")
            raise
    
    def compose_images(
        self, 
        image_paths: List[str], 
        prompt: str, 
        save_path: Optional[str] = None
    ) -> Tuple[bytes, Dict]:
        """
        Compose multiple images into a new image based on a prompt
        
        Args:
            image_paths: List of paths to input images (max 3 recommended)
            prompt: Text description of how to compose the images
            save_path: Optional path to save the composed image
            
        Returns:
            Tuple of (composed image data as bytes, metadata dict)
        """
        if len(image_paths) > 3:
            print("⚠️ Warning: Best performance with up to 3 images")
        
        print(f"🎭 Composing {len(image_paths)} images")
        print(f"📝 Composition prompt: {prompt[:100]}...")
        
        try:
            # Load and encode all input images
            parts = []
            for path in image_paths:
                with open(path, 'rb') as f:
                    image_data = f.read()
                
                encoded_image = base64.b64encode(image_data).decode('utf-8')
                parts.append({
                    "inline_data": {
                        "mime_type": self._get_mime_type(path),
                        "data": encoded_image
                    }
                })
            
            # Add the text prompt
            parts.append({"text": prompt})
            
            contents = [{"parts": parts}]
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents
            )
            
            # Extract usage metadata if available
            usage_metadata = None
            if hasattr(response, 'usage_metadata'):
                usage_metadata = response.usage_metadata
            
            # Extract composed image from response
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        # The data is already in bytes format, not base64 encoded
                        composed_data = part.inline_data.data if isinstance(part.inline_data.data, bytes) else base64.b64decode(part.inline_data.data)
                        
                        if save_path:
                            self._save_image(composed_data, save_path)
                        
                        # Track metadata and costs
                        metadata = {}
                        if self.track_costs:
                            metadata = self.tracker.save_generation_metadata(
                                operation="compose",
                                prompt=prompt,
                                image_path=save_path,
                                image_data=composed_data,
                                input_images=image_paths,
                                usage_metadata=usage_metadata
                            )
                            print(f"💰 Estimated cost: ${metadata['cost_usd']:.4f}")
                        
                        return composed_data, metadata
            
            raise ValueError("No composed image in response")
            
        except Exception as e:
            print(f"❌ Error composing images: {e}")
            raise
    
    def refine_image(
        self, 
        image_path: str, 
        refinement_prompt: str, 
        save_path: Optional[str] = None
    ) -> Tuple[bytes, Dict]:
        """
        Iteratively refine an image based on feedback
        
        Args:
            image_path: Path to the image to refine
            refinement_prompt: Specific refinement instructions
            save_path: Optional path to save the refined image
            
        Returns:
            Tuple of (refined image data as bytes, metadata dict)
        """
        print(f"🔧 Refining image: {image_path}")
        print(f"📝 Refinement: {refinement_prompt[:100]}...")
        
        # Use edit_image with refinement-specific prompt
        refined_prompt = f"Refine this image with the following changes: {refinement_prompt}"
        return self.edit_image(image_path, refined_prompt, save_path)
    
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
    
    def _save_image(self, image_data: bytes, path: str):
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
    
    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type based on file extension"""
        ext = Path(file_path).suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp'
        }
        return mime_types.get(ext, 'image/jpeg')


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
    
    3. USE STEP-BY-STEP INSTRUCTIONS:
       ✅ "First, add a mountain range in the background. Then, place a small cottage 
           in the foreground. Finally, add warm lighting from the cottage windows."
    
    4. SPECIFY STYLE AND MOOD:
       ✅ "In the style of watercolor painting with soft, dreamy colors"
       ✅ "Photorealistic with dramatic lighting and high contrast"
    
    5. FOR TEXT IN IMAGES:
       ✅ "Include the text 'HELLO WORLD' in bold, sans-serif font at the top"
    
    ==================================================
    """
    print(tips)


def show_cost_report(generator: GeminiImageGenerator, args):
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


def main():
    """Main function to run the image generator"""
    parser = argparse.ArgumentParser(
        description='Generate and edit images using Google Gemini API with cost tracking',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate a new image')
    gen_parser.add_argument('prompt', help='Text prompt for image generation')
    gen_parser.add_argument('-o', '--output', help='Output file path', 
                           default=f'generated_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
    
    # Edit command
    edit_parser = subparsers.add_parser('edit', help='Edit an existing image')
    edit_parser.add_argument('image', help='Path to input image')
    edit_parser.add_argument('prompt', help='Edit instructions')
    edit_parser.add_argument('-o', '--output', help='Output file path',
                            default=f'edited_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
    
    # Compose command
    comp_parser = subparsers.add_parser('compose', help='Compose multiple images')
    comp_parser.add_argument('images', nargs='+', help='Paths to input images')
    comp_parser.add_argument('-p', '--prompt', required=True, 
                            help='Composition instructions')
    comp_parser.add_argument('-o', '--output', help='Output file path',
                            default=f'composed_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
    
    # Refine command
    ref_parser = subparsers.add_parser('refine', help='Refine an image')
    ref_parser.add_argument('image', help='Path to image to refine')
    ref_parser.add_argument('prompt', help='Refinement instructions')
    ref_parser.add_argument('-o', '--output', help='Output file path',
                           default=f'refined_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
    
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
        generator = GeminiImageGenerator(
            api_key=args.api_key,
            track_costs=not args.no_tracking
        )
        
        # Execute command
        if args.command == 'generate':
            image_data, metadata = generator.generate_image(args.prompt, args.output)
            print(f"\n✅ Image generated successfully: {args.output}")
            if metadata:
                print(f"📊 Generation ID: {metadata['generation_id']}")
            
        elif args.command == 'edit':
            image_data, metadata = generator.edit_image(args.image, args.prompt, args.output)
            print(f"\n✅ Image edited successfully: {args.output}")
            if metadata:
                print(f"📊 Generation ID: {metadata['generation_id']}")
            
        elif args.command == 'compose':
            image_data, metadata = generator.compose_images(args.images, args.prompt, args.output)
            print(f"\n✅ Images composed successfully: {args.output}")
            if metadata:
                print(f"📊 Generation ID: {metadata['generation_id']}")
            
        elif args.command == 'refine':
            image_data, metadata = generator.refine_image(args.image, args.prompt, args.output)
            print(f"\n✅ Image refined successfully: {args.output}")
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
    main()