"""
Order Data Generator

This script creates a sample Excel file with randomized business order data.
The generated data includes detailed information about customers, products,
orders, and shipping for use in testing SAGE data quality metrics.
"""

import os
import sys
import random
import string
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import uuid

def generate_order_data(num_orders=150, output_path=None):
    """
    Generate detailed order data and save to Excel.
    
    Args:
        num_orders: Number of orders to generate
        output_path: Where to save the Excel file (auto-generated if None)
    
    Returns:
        Path to the generated Excel file
    """
    print(f"Generating detailed order data for {num_orders} orders...")
    
    # Create a directory for example data if it doesn't exist
    if output_path is None:
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        output_path = os.path.join(data_dir, f'business_orders_{datetime.now().strftime("%Y%m%d")}.xlsx')
    
    # Set random seed for reproducibility
    random.seed(42)
    np.random.seed(42)
    
    # ---------------------------------------------------------------------------
    # Define core data values
    # ---------------------------------------------------------------------------
    
    # Customer data
    customer_types = ['Individual', 'Small Business', 'Corporate', 'Government', 'Non-Profit']
    account_statuses = ['Active', 'VIP', 'New', 'At Risk', 'Inactive']
    countries = ['United States', 'Canada', 'United Kingdom', 'Australia', 'Germany', 'France', 'Japan', 'China']
    us_states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 
                'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
                'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT',
                'VA', 'WA', 'WV', 'WI', 'WY']
    
    # Product data
    categories = ['Electronics', 'Office Supplies', 'Furniture', 'Apparel', 'Food & Beverage']
    subcategories = {
        'Electronics': ['Computers', 'Phones', 'Accessories', 'Audio', 'Cameras'],
        'Office Supplies': ['Paper', 'Pens & Pencils', 'Organizers', 'Desk Accessories', 'Binders'],
        'Furniture': ['Desks', 'Chairs', 'Bookcases', 'Tables', 'Filing Cabinets'],
        'Apparel': ['Shirts', 'Pants', 'Outerwear', 'Footwear', 'Hats'],
        'Food & Beverage': ['Snacks', 'Beverages', 'Coffee & Tea', 'Candy', 'Meals']
    }
    manufacturers = ['TechCorp', 'OfficeWorld', 'FurnItAll', 'ThreadsInc', 'GoodEats', 'ElectraTech', 
                    'PaperPlus', 'ComfortSeating', 'StyleWear', 'SnackTime']
    
    # Order data
    order_sources = ['Website', 'Phone', 'Email', 'In-Store', 'Sales Rep', 'Partner']
    payment_methods = ['Credit Card', 'PayPal', 'Bank Transfer', 'Check', 'Purchase Order', 'Financing']
    payment_statuses = ['Paid', 'Pending', 'Partially Paid', 'Failed', 'Refunded']
    order_statuses = ['Completed', 'Processing', 'On Hold', 'Cancelled', 'Refunded']
    discount_types = ['None', 'Percentage', 'Fixed Amount', 'Buy One Get One', 'Loyalty Discount', 'Volume Discount']
    
    # Shipping data
    shipping_methods = ['Standard', 'Express', 'Overnight', 'Two-Day', 'International', 'Local Pickup']
    carriers = ['FedEx', 'UPS', 'USPS', 'DHL', 'Local Courier', 'Company Vehicle']
    fulfillment_centers = ['East Coast DC', 'West Coast DC', 'Central DC', 'International DC', 'Local Store']
    
    # Sales data
    sales_regions = ['Northeast', 'Southeast', 'Midwest', 'Southwest', 'West', 'International']
    sales_channels = ['Direct', 'Distributor', 'Retail Partner', 'Online Marketplace', 'Affiliate']
    sales_reps = [f"Rep-{i:03d}" for i in range(1, 21)]
    
    # ---------------------------------------------------------------------------
    # Generate Customer Data
    # ---------------------------------------------------------------------------
    
    num_customers = max(50, int(num_orders * 0.7))  # Some customers will have multiple orders
    customers = []
    
    for i in range(1, num_customers + 1):
        first_name = random.choice(['John', 'Jane', 'Michael', 'Emily', 'David', 'Sarah', 'Robert', 'Lisa', 
                                   'William', 'Elizabeth', 'James', 'Maria', 'Thomas', 'Jennifer', 'Charles', 
                                   'Karen', 'Joseph', 'Linda', 'Richard', 'Patricia'])
        last_name = random.choice(['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson', 
                                  'Moore', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin',
                                  'Thompson', 'Garcia', 'Martinez', 'Robinson'])
        
        # Generate company name for non-individual customers
        if random.random() < 0.7:  # 70% chance of being a business
            company_names_first = ['Global', 'National', 'Premier', 'Elite', 'Advanced', 'Summit', 'Core', 'Prime', 'Central', 'Dynamic']
            company_names_mid = ['Tech', 'Biz', 'Office', 'Market', 'Trade', 'Retail', 'Supply', 'Service', 'Solutions', 'Systems']
            company_names_last = ['Inc', 'LLC', 'Corp', 'Co', 'International', 'Group', 'Partners', 'Associates', 'Enterprises', 'Industries']
            company_name = f"{random.choice(company_names_first)} {random.choice(company_names_mid)} {random.choice(company_names_last)}"
        else:
            company_name = None
        
        customer_type = random.choice(customer_types)
        account_status = random.choice(account_statuses)
        
        # Generate address
        country = random.choice(countries)
        if country == 'United States':
            state = random.choice(us_states)
            zip_code = f"{random.randint(10000, 99999)}"
        else:
            state = None
            zip_code = ''.join(random.choices(string.digits + string.ascii_uppercase, k=6))
        
        address_street = f"{random.randint(1, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Maple', 'Cedar', 'Elm', 'Washington', 'Lake'])} {random.choice(['St', 'Ave', 'Blvd', 'Rd', 'Dr', 'Ln', 'Way', 'Pl'])}"
        city = random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Francisco'])
        
        # Generate contact info
        email = f"{first_name.lower()}.{last_name.lower()}{''.join(random.choices(string.digits, k=2))}@{random.choice(['example.com', 'business.net', 'mycompany.org', 'mail.com'])}"
        phone = f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        
        # Create customer record
        customer = {
            'customer_id': i,
            'customer_uuid': str(uuid.uuid4()),
            'first_name': first_name,
            'last_name': last_name,
            'company_name': company_name,
            'customer_type': customer_type,
            'account_status': account_status,
            'email': email,
            'phone': phone,
            'address': address_street,
            'city': city,
            'state': state,
            'zip_code': zip_code,
            'country': country,
            'registration_date': (datetime.now() - timedelta(days=random.randint(30, 1095))).strftime('%Y-%m-%d'),
            'last_purchase_date': (datetime.now() - timedelta(days=random.randint(0, 180))).strftime('%Y-%m-%d'),
            'total_orders': random.randint(1, 50),
            'lifetime_value': round(random.uniform(100, 50000), 2),
            'credit_limit': random.choice([1000, 2000, 5000, 10000, 25000, 50000, None]),
            'payment_terms': random.choice(['Net 30', 'Net 15', 'Net 45', 'Due on Receipt', 'Prepaid']),
            'notes': random.choice(['VIP Customer', 'Requires special handling', 'Tax exempt', 'Credit hold', 'Previous returns', None, None, None, None])
        }
        
        # Introduce data quality issues in ~5% of records
        if random.random() < 0.05:
            issue_type = random.randint(1, 5)
            if issue_type == 1:
                # Missing email
                customer['email'] = None
            elif issue_type == 2:
                # Invalid phone format
                customer['phone'] = f"{random.randint(100, 999)}{random.randint(1000000, 9999999)}"
            elif issue_type == 3:
                # Missing address components
                customer['address'] = None
            elif issue_type == 4:
                # Inconsistent date format
                customer['registration_date'] = (datetime.now() - timedelta(days=random.randint(30, 1095))).strftime('%m/%d/%Y')
            elif issue_type == 5:
                # Negative value
                customer['lifetime_value'] = -1 * customer['lifetime_value']
        
        customers.append(customer)
    
    # ---------------------------------------------------------------------------
    # Generate Product Data
    # ---------------------------------------------------------------------------
    
    num_products = 100
    products = []
    
    for i in range(1, num_products + 1):
        category = random.choice(categories)
        subcategory = random.choice(subcategories[category])
        
        manufacturer = random.choice(manufacturers)
        
        # Generate product name
        adjectives = ['Premium', 'Basic', 'Advanced', 'Deluxe', 'Standard', 'Professional', 'Commercial', 'Economy']
        product_name = f"{random.choice(adjectives)} {subcategory} {random.choice(['Pro', 'Plus', 'Max', 'Lite', 'Ultra', ''])}"
        
        # Create product record
        product = {
            'product_id': i,
            'product_sku': f"{category[:2].upper()}{subcategory[:2].upper()}-{random.randint(1000, 9999)}",
            'product_name': product_name,
            'description': f"{manufacturer} {product_name} - High-quality {subcategory.lower()} for professional use",
            'category': category,
            'subcategory': subcategory,
            'manufacturer': manufacturer,
            'supplier': random.choice(['DirectSupply Inc', 'GlobalSource Ltd', 'PremierVendors', 'RegionalDistro', 'ImportExport Co']),
            'unit_cost': round(random.uniform(10, 500), 2),
            'unit_price': round(random.uniform(15, 1000), 2),
            'minimum_price': round(random.uniform(10, 400), 2),
            'msrp': round(random.uniform(20, 1200), 2),
            'weight_lbs': round(random.uniform(0.1, 100), 2),
            'dimensions': f"{random.randint(1, 50)}x{random.randint(1, 50)}x{random.randint(1, 50)}",
            'color': random.choice(['Black', 'White', 'Gray', 'Silver', 'Blue', 'Red', 'Brown', 'Green']),
            'current_stock': random.randint(0, 1000),
            'reorder_level': random.randint(5, 100),
            'reorder_quantity': random.randint(10, 200),
            'lead_time_days': random.randint(1, 60),
            'is_taxable': random.choice([True, True, True, False]),  # 75% taxable
            'is_active': random.choice([True, True, True, True, False]),  # 80% active
            'discontinued': random.choice([False, False, False, False, True])  # 20% discontinued
        }
        
        # Set profit margin and calculate other price fields
        base_margin = random.uniform(0.2, 0.6)  # 20-60% margin
        if product['unit_cost'] * (1 + base_margin) > product['unit_price']:
            product['unit_price'] = round(product['unit_cost'] * (1 + base_margin), 2)
        
        # Ensure minimum price is less than unit price
        if product['minimum_price'] >= product['unit_price']:
            product['minimum_price'] = round(product['unit_price'] * 0.9, 2)
        
        # Ensure MSRP is higher than unit price
        if product['msrp'] <= product['unit_price']:
            product['msrp'] = round(product['unit_price'] * 1.2, 2)
        
        # Introduce data quality issues in ~5% of records
        if random.random() < 0.05:
            issue_type = random.randint(1, 5)
            if issue_type == 1:
                # Negative inventory
                product['current_stock'] = -random.randint(1, 10)
            elif issue_type == 2:
                # Price lower than cost
                product['unit_price'] = product['unit_cost'] * random.uniform(0.5, 0.9)
            elif issue_type == 3:
                # Missing manufacturer
                product['manufacturer'] = None
            elif issue_type == 4:
                # Invalid dimensions format
                product['dimensions'] = f"{random.randint(1, 50)} x {random.randint(1, 50)}"
            elif issue_type == 5:
                # Inconsistent category/subcategory
                product['subcategory'] = random.choice(subcategories[random.choice(categories)])
        
        products.append(product)
    
    # ---------------------------------------------------------------------------
    # Generate Order Data
    # ---------------------------------------------------------------------------
    
    orders = []
    order_items = []
    order_item_id = 1
    
    for i in range(1, num_orders + 1):
        # Select customer
        customer = random.choice(customers)
        
        # Generate order dates
        order_date = datetime.now() - timedelta(days=random.randint(1, 365))
        ship_date = order_date + timedelta(days=random.randint(1, 10))
        delivery_date = ship_date + timedelta(days=random.randint(1, 7))
        
        # Handle cancelled/refunded orders
        order_status = random.choices(
            order_statuses, 
            weights=[0.7, 0.15, 0.05, 0.05, 0.05],  # 70% completed, 15% processing, 5% each for others
            k=1
        )[0]
        
        if order_status in ['Cancelled', 'Refunded']:
            ship_date = None
            delivery_date = None
        
        # Generate order details
        order_source = random.choice(order_sources)
        payment_method = random.choice(payment_methods)
        payment_status = random.choice(payment_statuses)
        
        # If cancelled/refunded, adjust payment status accordingly
        if order_status == 'Cancelled':
            payment_status = random.choice(['Refunded', 'None'])
        elif order_status == 'Refunded':
            payment_status = 'Refunded'
        
        # Generate shipping information
        shipping_method = random.choice(shipping_methods)
        carrier = random.choice(carriers)
        fulfillment_center = random.choice(fulfillment_centers)
        
        # Generate tracking number if shipped
        if ship_date and order_status not in ['Cancelled', 'Refunded']:
            tracking_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        else:
            tracking_number = None
        
        # Generate sales information
        sales_region = random.choice(sales_regions)
        sales_channel = random.choice(sales_channels)
        sales_rep = random.choice(sales_reps)
        
        # Decide on discount
        discount_type = random.choices(
            discount_types, 
            weights=[0.6, 0.1, 0.1, 0.05, 0.05, 0.1],  # 60% no discount
            k=1
        )[0]
        
        if discount_type == 'None':
            discount_amount = 0
            discount_pct = 0
        elif discount_type == 'Percentage':
            discount_pct = random.choice([5, 10, 15, 20, 25, 30])
            discount_amount = 0  # Will be calculated after items are added
        elif discount_type == 'Fixed Amount':
            discount_amount = random.choice([10, 25, 50, 100])
            discount_pct = 0
        else:
            # Other discount types
            discount_amount = random.choice([0, 10, 25, 50])
            discount_pct = random.choice([0, 5, 10, 15])
        
        # Create order record (subtotal will be calculated after adding items)
        order = {
            'order_id': i,
            'order_number': f"ORD-{datetime.now().year}-{i:05d}",
            'order_uuid': str(uuid.uuid4()),
            'customer_id': customer['customer_id'],
            'customer_name': f"{customer['first_name']} {customer['last_name']}",
            'company_name': customer['company_name'],
            'order_date': order_date.strftime('%Y-%m-%d'),
            'order_time': order_date.strftime('%H:%M:%S'),
            'order_status': order_status,
            'order_source': order_source,
            'payment_method': payment_method,
            'payment_status': payment_status,
            'subtotal': 0,  # Will be calculated
            'shipping_cost': round(random.uniform(5, 50), 2),
            'tax_rate': round(random.uniform(0.05, 0.095), 3),
            'tax_amount': 0,  # Will be calculated
            'discount_type': discount_type,
            'discount_amount': discount_amount,
            'discount_pct': discount_pct,
            'total_amount': 0,  # Will be calculated
            'currency': 'USD',
            'shipping_method': shipping_method,
            'carrier': carrier,
            'tracking_number': tracking_number,
            'fulfillment_center': fulfillment_center,
            'ship_date': ship_date.strftime('%Y-%m-%d') if ship_date else None,
            'delivery_date': delivery_date.strftime('%Y-%m-%d') if delivery_date else None,
            'shipping_address': customer['address'],
            'shipping_city': customer['city'],
            'shipping_state': customer['state'],
            'shipping_zip': customer['zip_code'],
            'shipping_country': customer['country'],
            'billing_address': customer['address'],  # Same as shipping for simplicity
            'billing_city': customer['city'],
            'billing_state': customer['state'],
            'billing_zip': customer['zip_code'],
            'billing_country': customer['country'],
            'sales_region': sales_region,
            'sales_channel': sales_channel,
            'sales_rep': sales_rep,
            'customer_po': f"PO-{random.randint(10000, 99999)}" if random.random() < 0.3 else None,
            'notes': random.choice([
                'Rush order', 'Special packaging required', 'Customer requested delivery notification',
                'Fragile items', 'Gift wrapping requested', None, None, None, None, None
            ])
        }
        
        # Generate a random number of items for this order (1-10)
        num_items = random.randint(1, 10)
        order_subtotal = 0
        
        # Add items to the order
        for j in range(num_items):
            # Select a random product
            product = random.choice(products)
            
            # Determine quantity
            quantity = random.randint(1, 20)
            
            # Calculate item price and discounts
            unit_price = product['unit_price']
            
            # Apply random pricing adjustments in some cases
            if random.random() < 0.1:  # 10% chance of custom pricing
                unit_price = random.uniform(product['minimum_price'], product['msrp'])
            
            # Calculate line item values
            line_item_subtotal = quantity * unit_price
            
            # Apply item-specific discount in some cases
            item_discount_pct = 0
            if random.random() < 0.2:  # 20% chance of item-specific discount
                item_discount_pct = random.choice([5, 10, 15, 20])
                line_item_discount = line_item_subtotal * (item_discount_pct / 100)
            else:
                line_item_discount = 0
            
            line_item_total = line_item_subtotal - line_item_discount
            order_subtotal += line_item_total
            
            # Create order item record
            item = {
                'order_item_id': order_item_id,
                'order_id': order['order_id'],
                'order_number': order['order_number'],
                'product_id': product['product_id'],
                'product_sku': product['product_sku'],
                'product_name': product['product_name'],
                'quantity': quantity,
                'unit_price': round(unit_price, 2),
                'unit_cost': round(product['unit_cost'], 2),
                'subtotal': round(line_item_subtotal, 2),
                'discount_pct': item_discount_pct,
                'discount_amount': round(line_item_discount, 2),
                'line_total': round(line_item_total, 2),
                'is_taxable': product['is_taxable'],
                'tax_rate': order['tax_rate'] if product['is_taxable'] else 0,
                'tax_amount': round(line_item_total * order['tax_rate'], 2) if product['is_taxable'] else 0,
                'fulfillment_status': 'Shipped' if order_status == 'Completed' else order_status,
                'category': product['category'],
                'manufacturer': product['manufacturer'],
                'profit_margin': round((unit_price - product['unit_cost']) / unit_price * 100, 2),
                'profit_amount': round((unit_price - product['unit_cost']) * quantity, 2)
            }
            
            order_items.append(item)
            order_item_id += 1
        
        # Update order with calculated totals
        order['subtotal'] = round(order_subtotal, 2)
        
        # Apply order discount if applicable
        if discount_type == 'Percentage':
            order['discount_amount'] = round(order_subtotal * (discount_pct / 100), 2)
        
        # Calculate taxable amount (after discounts)
        taxable_amount = order_subtotal - order['discount_amount']
        order['tax_amount'] = round(taxable_amount * order['tax_rate'], 2)
        
        # Calculate total amount
        order['total_amount'] = round(order['subtotal'] - order['discount_amount'] + order['tax_amount'] + order['shipping_cost'], 2)
        
        # Introduce data quality issues in ~5% of records
        if random.random() < 0.05:
            issue_type = random.randint(1, 5)
            if issue_type == 1:
                # Inconsistent date format
                order['order_date'] = order_date.strftime('%m/%d/%Y')
            elif issue_type == 2:
                # Negative total amount
                order['total_amount'] = -order['total_amount']
            elif issue_type == 3:
                # Missing customer information
                order['customer_name'] = None
            elif issue_type == 4:
                # Shipping before order date
                if order['ship_date']:
                    order['ship_date'] = (order_date - timedelta(days=random.randint(1, 5))).strftime('%Y-%m-%d')
            elif issue_type == 5:
                # Mathematical inconsistency
                order['total_amount'] = round(order['total_amount'] * random.uniform(0.9, 1.1), 2)
        
        orders.append(order)
    
    # ---------------------------------------------------------------------------
    # Save data to Excel
    # ---------------------------------------------------------------------------
    
    # Convert lists to DataFrames
    df_customers = pd.DataFrame(customers)
    df_products = pd.DataFrame(products)
    df_orders = pd.DataFrame(orders)
    df_order_items = pd.DataFrame(order_items)
    
    # Create summary calculations
    summary_data = {
        'metric': [
            'Total Orders', 'Total Revenue', 'Average Order Value', 'Total Items Sold',
            'Items Per Order', 'Total Customers', 'New Customers', 'Returning Customers',
            'Total Products', 'Product Categories', 'Revenue by Category', 'Top Sales Region',
            'Top Sales Channel', 'Top Sales Rep', 'Top Product', 'Top Customer'
        ],
        'value': [
            len(df_orders),
            f"${df_orders['total_amount'].sum():,.2f}",
            f"${df_orders['total_amount'].mean():,.2f}",
            df_order_items['quantity'].sum(),
            f"{df_order_items.groupby('order_id')['quantity'].sum().mean():.2f}",
            len(df_customers),
            f"{len(df_customers[pd.to_datetime(df_customers['registration_date'], format='mixed') > datetime.now() - timedelta(days=90)])} (last 90 days)",
            len(df_customers) - len(df_customers[pd.to_datetime(df_customers['registration_date'], format='mixed') > datetime.now() - timedelta(days=90)]),
            len(df_products),
            len(df_products['category'].unique()),
            df_order_items.groupby('category')['line_total'].sum().idxmax(),
            df_orders.groupby('sales_region')['total_amount'].sum().idxmax(),
            df_orders.groupby('sales_channel')['total_amount'].sum().idxmax(),
            df_orders.groupby('sales_rep')['total_amount'].sum().idxmax(),
            df_order_items.groupby('product_name')['line_total'].sum().idxmax(),
            df_orders.groupby('customer_name')['total_amount'].sum().idxmax()
        ],
        'notes': [
            f"For the period {pd.to_datetime(df_orders['order_date'], format='mixed').min().strftime('%Y-%m-%d')} to {pd.to_datetime(df_orders['order_date'], format='mixed').max().strftime('%Y-%m-%d')}",
            f"${df_orders['total_amount'].sum() / num_orders:,.2f} per order avg.",
            f"${df_orders['total_amount'].median():,.2f} median order value",
            f"{df_order_items.groupby('product_id')['quantity'].count().mean():.2f} items sold per product avg.",
            f"{df_order_items.groupby('order_id')['quantity'].sum().max()} max items in a single order",
            f"{df_orders.groupby('customer_id').size().mean():.2f} orders per customer avg.",
            "New customers registered within last 90 days",
            "Customers with a registration date older than 90 days",
            f"{len(df_products[df_products['is_active']])} active products",
            ", ".join(df_products['category'].unique()),
            f"${df_order_items.groupby('category')['line_total'].sum().max():,.2f} total revenue",
            f"${df_orders[df_orders['sales_region'] == df_orders.groupby('sales_region')['total_amount'].sum().idxmax()]['total_amount'].sum():,.2f}",
            f"${df_orders[df_orders['sales_channel'] == df_orders.groupby('sales_channel')['total_amount'].sum().idxmax()]['total_amount'].sum():,.2f}",
            f"${df_orders[df_orders['sales_rep'] == df_orders.groupby('sales_rep')['total_amount'].sum().idxmax()]['total_amount'].sum():,.2f}",
            f"${df_order_items[df_order_items['product_name'] == df_order_items.groupby('product_name')['line_total'].sum().idxmax()]['line_total'].sum():,.2f}",
            f"${df_orders[df_orders['customer_name'] == df_orders.groupby('customer_name')['total_amount'].sum().idxmax()]['total_amount'].sum():,.2f}"
        ]
    }
    df_summary = pd.DataFrame(summary_data)
    
    # Save to Excel file
    print(f"Saving data to {output_path}...")
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df_orders.to_excel(writer, sheet_name='Orders', index=False)
        df_order_items.to_excel(writer, sheet_name='Order Items', index=False)
        df_customers.to_excel(writer, sheet_name='Customers', index=False)
        df_products.to_excel(writer, sheet_name='Products', index=False)
        df_summary.to_excel(writer, sheet_name='Summary', index=False)
        
    print(f"Excel file with detailed order data saved to: {output_path}")
    print(f"  - Created {len(df_orders)} orders")
    print(f"  - Created {len(df_order_items)} order items")
    print(f"  - Created {len(df_customers)} customers")
    print(f"  - Created {len(df_products)} products")
    print(f"  - Total revenue: ${df_orders['total_amount'].sum():,.2f}")
    
    # Return the path to the generated file
    return output_path

def main():
    """
    Main function to run the script.
    """
    print("=" * 80)
    print("SAGE Example: Business Order Data Generator")
    print("=" * 80)
    
    # Ask user for the number of orders to generate
    num_orders_input = input("Enter number of orders to generate (default: 150): ")
    try:
        num_orders = int(num_orders_input) if num_orders_input.strip() else 150
    except ValueError:
        print("Invalid input. Using default of 150 orders.")
        num_orders = 150
    
    # Ask if user wants to specify output path
    custom_path = input("Do you want to specify a custom output path? (y/n, default: n): ").lower().startswith('y')
    
    if custom_path:
        output_path = input("Enter output path (including filename.xlsx): ")
        # Ensure path has .xlsx extension
        if not output_path.endswith('.xlsx'):
            output_path += '.xlsx'
    else:
        output_path = None
    
    # Generate data
    file_path = generate_order_data(num_orders, output_path)
    
    # Ask user if they want to analyze the data with SAGE
    analyze = input("\nDo you want to analyze this file with SAGE? (y/n): ").lower().startswith('y')
    
    if analyze:
        # Import the grade_excel_file script and run analysis
        try:
            # Add the folder containing this script to the path
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            
            # Import the grade_excel_file module
            from grade_excel_file import main as analyze_main
            
            # Set sys.argv to pass the file path to the analysis script
            sys.argv = ['grade_excel_file.py', file_path]
            
            # Run the analysis
            print("\nStarting data quality analysis...\n")
            analyze_main()
        except ImportError:
            print("\nCould not import the grade_excel_file module.")
            print(f"You can analyze the file manually by running:")
            print(f"python grade_excel_file.py {file_path}")
        except Exception as e:
            print(f"\nError running analysis: {e}")

if __name__ == "__main__":
    main()
