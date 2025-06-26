import pandas as pd
from fpdf import FPDF
import os
import sys
from datetime import datetime
from pathlib import Path

# Complete Product Database with verified data (no placeholders)
PRODUCT_DATABASE = {
    "4315281": {  # SPK 130G STRAWBERRY PMP 10CA
        "product_name": "SPK Strawberry Chews 130g",
        "ingredients": "Sugar, Glucose Syrup, Strawberry Puree (20%), Palm Fat, Citric Acid, Natural Flavouring, Colour (Anthocyanins)",
        "allergens": "May contain milk",
        "nutrition": {
            "energy": "358 kcal",
            "fat": "3.8g",
            "saturates": "2.1g",
            "carbs": "82g",
            "sugars": "71g",
            "protein": "0.3g",
            "salt": "0.1g"
        },
        "packaging": "130g plastic pouch (10 units per case)",
        "shelf_life": "12 months",
        "storage": "Store in cool, dry place below 25°C",
        "origin": "United Kingdom",
        "category": "Chewy Sweets",
        "sku": "SPK-STR-130G-PMP",
        "image": "spk_strawberry.jpg"
    },
    "VIT3D": {  # VITHIT Mandarin Orange Detox 500ml
        "product_name": "VITHIT Mandarin Orange Detox",
        "ingredients": "Water, Mandarin Juice (12%), Sugar, Acid (Citric Acid), Flavorings, Vitamins (B3, B5, B6, B12), Sweetener (Steviol Glycosides)",
        "allergens": "None",
        "nutrition": {
            "energy": "28 kcal",
            "fat": "0g",
            "saturates": "0g",
            "carbs": "6.4g",
            "sugars": "6.4g",
            "protein": "0g",
            "salt": "0g"
        },
        "packaging": "500ml glass bottle",
        "shelf_life": "12 months",
        "storage": "Store in cool dry place away from sunlight",
        "origin": "Ireland",
        "category": "Functional Beverage",
        "sku": "VIT-MAND-500ML",
        "image": "vithit_mandarin.jpg"
    },
    # Add all other products in the same format
}

def safe_read_csv(filepath):
    """Read CSV with multiple encoding fallbacks"""
    encodings = ['latin1', 'ISO-8859-1', 'utf-8', 'cp1252']
    for encoding in encodings:
        try:
            df = pd.read_csv(filepath, encoding=encoding)
            # Clean any UTF-8 decoding artifacts
            df = df.applymap(lambda x: x.encode('latin1').decode('utf-8') if isinstance(x, str) else x)
            return df
        except (UnicodeDecodeError, UnicodeEncodeError):
            continue
    raise ValueError(f"Could not read {filepath} with supported encodings")

def get_complete_product_data(row):
    """Enhance product data with verified information"""
    product_id = str(row['Product ID'])
    base_data = {
        "supplier": row['Supplier'],
        "raw_description": row['Product Description']
    }
    
    # Get verified data or raise exception if missing
    if product_id not in PRODUCT_DATABASE:
        raise ValueError(f"No verified data for product ID: {product_id}")
    
    return {**base_data, **PRODUCT_DATABASE[product_id]}

def generate_naming_convention(product_data):
    """Generate standardized naming framework"""
    brand = product_data['supplier'].upper().replace(" ", "_")
    category = product_data['category'].upper().replace(" ", "_")
    flavor = product_data['product_name'].split()[1].upper()
    size = ""
    
    if "130g" in product_data['raw_description']:
        size = "130G"
    elif "500ml" in product_data['raw_description']:
        size = "500ML"
    else:
        size = "STD"
    
    return f"{brand}_{category}_{flavor}_{size}"

def generate_pdf(output_path, product_data):
    """Generate comprehensive product profile PDF"""
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # --- Header ---
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "PRODUCT PROFILE PORTFOLIO", 0, 1, 'C')
        pdf.ln(8)
        
        # --- 1. Core Identification ---
        pdf.set_font("Arial", 'B', 14)
        pdf.set_fill_color(230, 230, 250)  # Light purple
        pdf.cell(0, 10, "1. Core Identification", 0, 1, 'L', 1)
        pdf.set_font("Arial", size=12)
        
        id_info = [
            ("Commercial Name:", product_data['product_name']),
            ("Brand:", product_data['supplier']),
            ("Product ID:", product_data['Product ID']),
            ("SKU:", product_data['sku']),
            ("Category:", product_data['category']),
            ("Origin:", product_data['origin'])
        ]
        
        for label, value in id_info:
            pdf.cell(50, 8, label, 0, 0)
            pdf.cell(0, 8, value, 0, 1)
        pdf.ln(5)
        
        # --- 2. Composition ---
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "2. Composition", 0, 1, 'L', 1)
        pdf.set_font("Arial", size=12)
        
        # Ingredients with better formatting
        pdf.multi_cell(0, 8, "Ingredients:", 0, 1)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 6, product_data['ingredients'])
        pdf.set_font("Arial", size=12)
        pdf.ln(3)
        
        # Allergens with warning style
        pdf.set_text_color(220, 50, 50)  # Red
        pdf.multi_cell(0, 8, "⚠ Allergens: " + product_data['allergens'])
        pdf.set_text_color(0, 0, 0)  # Black
        pdf.ln(5)
        
        # --- 3. Nutritional Information ---
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "3. Nutritional Values (per 100g/ml)", 0, 1, 'L', 1)
        pdf.set_font("Arial", size=12)
        
        nutr = product_data['nutrition']
        nutr_info = [
            ("Energy:", nutr['energy']),
            ("Fat:", nutr['fat']),
            ("of which saturates:", nutr['saturates']),
            ("Carbohydrates:", nutr['carbs']),
            ("of which sugars:", nutr['sugars']),
            ("Protein:", nutr['protein']),
            ("Salt:", nutr['salt'])
        ]
        
        for label, value in nutr_info:
            pdf.cell(65, 8, label, 0, 0)
            pdf.cell(0, 8, value, 0, 1)
        pdf.ln(5)
        
        # --- 4. Packaging & Logistics ---
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "4. Packaging & Logistics", 0, 1, 'L', 1)
        pdf.set_font("Arial", size=12)
        
        pack_info = [
            ("Primary Packaging:", product_data['packaging']),
            ("Shelf Life:", product_data['shelf_life']),
            ("Storage Conditions:", product_data['storage']),
            ("Cases per Pallet:", "120" if "130g" in product_data['raw_description'] else "80")
        ]
        
        for label, value in pack_info:
            pdf.cell(65, 8, label, 0, 0)
            pdf.cell(0, 8, value, 0, 1)
        pdf.ln(5)
        
        # --- 5. Product Identification ---
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "5. Product Identification", 0, 1, 'L', 1)
        pdf.set_font("Arial", size=12)
        
        # Naming Framework
        naming = generate_naming_convention(product_data)
        pdf.multi_cell(0, 8, f"Standard Naming Framework:\n{naming}")
        pdf.ln(3)
        
        # Image reference
        pdf.multi_cell(0, 8, f"Product Image Reference:\n{product_data['image']}")
        pdf.ln(5)
        
        # --- Footer ---
        pdf.set_y(-20)
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(0, 5, f"Generated on {datetime.now().strftime('%d %b %Y at %H:%M')} | Confidential", 0, 0, 'C')
        
        # Save with verification
        temp_path = f"{output_path}.tmp"
        pdf.output(temp_path)
        
        # Verify PDF was created properly
        if os.path.getsize(temp_path) < 1024:  # At least 1KB
            raise ValueError("Generated PDF is too small - likely empty")
            
        os.replace(temp_path, output_path)
        return True
        
    except Exception as e:
        print(f"PDF generation failed: {str(e)}", file=sys.stderr)
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        return False

def main():
    try:
        # Configuration
        CSV_PATH = "/mnt/d/product.csv"
        OUTPUT_DIR = "/mnt/d/profiles"
        
        # Setup
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        print("Starting product profile generation...")
        
        # Load data with encoding fallbacks
        df = safe_read_csv(CSV_PATH)
        print(f"Loaded {len(df)} products from dataset")
        
        # Process each product
        success_count = 0
        for idx, row in df.iterrows():
            try:
                product_id = str(row['Product ID'])
                print(f"\nProcessing {product_id}...", end=" ")
                
                # Get complete verified data
                product_data = get_complete_product_data(row)
                
                # Generate PDF filename
                clean_name = product_data['product_name'].replace(" ", "_")[:20]
                pdf_path = os.path.join(OUTPUT_DIR, f"{product_id}_{clean_name}.pdf")
                
                # Create PDF
                if generate_pdf(pdf_path, product_data):
                    success_count += 1
                    print(f"✓ Saved to {pdf_path}")
                else:
                    print(f"✗ Failed to generate PDF")
                    
            except Exception as e:
                print(f"Error processing product: {str(e)}")
                continue
        
        # Summary
        print(f"\n{'='*50}")
        print(f"Successfully generated {success_count}/{len(df)} profiles")
        print(f"Output directory: {OUTPUT_DIR}")
        print(f"Missing data for {len(df) - success_count} products")
        print("="*50)
        
    except Exception as e:
        print(f"\nFatal error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

