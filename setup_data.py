#!/usr/bin/env python
"""
FleetFlow Database Setup Script
This script creates initial data for the FleetFlow application.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleetflow.settings')
django.setup()

from django.contrib.auth import get_user_model
from vehicles.models import VehicleType, Vehicle
from drivers.models import Driver
from maintenance.models import MaintenanceType
from fuel.models import FuelStation

User = get_user_model()

def create_initial_users():
    """Create initial users with different roles"""
    print("Creating initial users...")
    
    users_data = [
        {
            'username': 'admin',
            'email': 'admin@fleetflow.com',
            'first_name': 'System',
            'last_name': 'Administrator',
            'role': 'admin',
            'password': 'admin123'
        },
        {
            'username': 'manager',
            'email': 'manager@fleetflow.com',
            'first_name': 'Fleet',
            'last_name': 'Manager',
            'role': 'fleet_manager',
            'password': 'manager123'
        },
        {
            'username': 'dispatcher',
            'email': 'dispatcher@fleetflow.com',
            'first_name': 'Trip',
            'last_name': 'Dispatcher',
            'role': 'dispatcher',
            'password': 'dispatch123'
        },
        {
            'username': 'safety',
            'email': 'safety@fleetflow.com',
            'first_name': 'Safety',
            'last_name': 'Officer',
            'role': 'safety_officer',
            'password': 'safety123'
        },
        {
            'username': 'analyst',
            'email': 'analyst@fleetflow.com',
            'first_name': 'Financial',
            'last_name': 'Analyst',
            'role': 'financial_analyst',
            'password': 'analyst123'
        }
    ]
    
    for user_data in users_data:
        if not User.objects.filter(username=user_data['username']).exists():
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data['role'],
                password=user_data['password']
            )
            print(f"Created user: {user.username} ({user.get_role_display()})")
        else:
            print(f"User {user_data['username']} already exists")


def create_vehicle_types():
    """Create initial vehicle types"""
    print("Creating vehicle types...")
    
    vehicle_types = [
        {'name': 'Light Truck', 'description': 'Small delivery trucks up to 3.5 tons'},
        {'name': 'Medium Truck', 'description': 'Medium duty trucks 3.5-7.5 tons'},
        {'name': 'Heavy Truck', 'description': 'Heavy duty trucks over 7.5 tons'},
        {'name': 'Van', 'description': 'Cargo vans for small deliveries'},
        {'name': 'Refrigerated Truck', 'description': 'Temperature-controlled vehicles'},
        {'name': 'Flatbed Truck', 'description': 'Open bed trucks for oversized cargo'},
        {'name': 'Tanker Truck', 'description': 'Liquid transport vehicles'},
    ]
    
    for vt_data in vehicle_types:
        if not VehicleType.objects.filter(name=vt_data['name']).exists():
            vt = VehicleType.objects.create(**vt_data)
            print(f"Created vehicle type: {vt.name}")
        else:
            print(f"Vehicle type {vt_data['name']} already exists")


def create_maintenance_types():
    """Create initial maintenance types"""
    print("Creating maintenance types...")
    
    maintenance_types = [
        {'name': 'Oil Change', 'description': 'Regular oil and filter change', 'estimated_duration_hours': 1},
        {'name': 'Tire Service', 'description': 'Tire rotation and replacement', 'estimated_duration_hours': 2},
        {'name': 'Brake Service', 'description': 'Brake inspection and replacement', 'estimated_duration_hours': 3},
        {'name': 'Engine Service', 'description': 'Major engine maintenance', 'estimated_duration_hours': 8},
        {'name': 'Transmission Service', 'description': 'Transmission fluid and inspection', 'estimated_duration_hours': 4},
        {'name': 'Annual Inspection', 'description': 'Annual safety inspection', 'estimated_duration_hours': 2},
        {'name': 'AC Service', 'description': 'Air conditioning service', 'estimated_duration_hours': 2},
        {'name': 'Electrical Service', 'description': 'Electrical system diagnosis', 'estimated_duration_hours': 3},
    ]
    
    for mt_data in maintenance_types:
        if not MaintenanceType.objects.filter(name=mt_data['name']).exists():
            mt = MaintenanceType.objects.create(**mt_data)
            print(f"Created maintenance type: {mt.name}")
        else:
            print(f"Maintenance type {mt_data['name']} already exists")


def create_fuel_stations():
    """Create initial fuel stations"""
    print("Creating fuel stations...")
    
    fuel_stations = [
        {
            'name': 'Shell Station Downtown',
            'address': '123 Main St',
            'city': 'New York',
            'state': 'NY',
            'postal_code': '10001',
            'phone': '+1-212-555-0101'
        },
        {
            'name': 'BP Highway Stop',
            'address': '456 Highway 1',
            'city': 'Los Angeles',
            'state': 'CA',
            'postal_code': '90001',
            'phone': '+1-213-555-0202'
        },
        {
            'name': 'Exxon Fleet Center',
            'address': '789 Industrial Blvd',
            'city': 'Chicago',
            'state': 'IL',
            'postal_code': '60007',
            'phone': '+1-312-555-0303'
        }
    ]
    
    for fs_data in fuel_stations:
        if not FuelStation.objects.filter(name=fs_data['name']).exists():
            fs = FuelStation.objects.create(**fs_data)
            print(f"Created fuel station: {fs.name}")
        else:
            print(f"Fuel station {fs_data['name']} already exists")


def create_sample_vehicles():
    """Create sample vehicles"""
    print("Creating sample vehicles...")
    
    # Get vehicle types
    light_truck = VehicleType.objects.get(name='Light Truck')
    medium_truck = VehicleType.objects.get(name='Medium Truck')
    van = VehicleType.objects.get(name='Van')
    
    vehicles_data = [
        {
            'name': 'Delivery Van 001',
            'vehicle_type': van,
            'model': 'Ford Transit',
            'license_plate': 'ABC-1234',
            'vin': '1FTBW2CM5EKA12345',
            'capacity': 1500.00,
            'fuel_capacity': 80.00,
            'status': 'available'
        },
        {
            'name': 'Heavy Truck 001',
            'vehicle_type': medium_truck,
            'model': 'Freightliner Cascadia',
            'license_plate': 'XYZ-5678',
            'vin': '1FUJGBDV1ELSA23456',
            'capacity': 8000.00,
            'fuel_capacity': 300.00,
            'status': 'available'
        },
        {
            'name': 'City Truck 001',
            'vehicle_type': light_truck,
            'model': 'Isuzu NQR',
            'license_plate': 'DEF-9012',
            'vin': 'JALC4V150E70034567',
            'capacity': 3500.00,
            'fuel_capacity': 120.00,
            'status': 'available'
        }
    ]
    
    for v_data in vehicles_data:
        if not Vehicle.objects.filter(license_plate=v_data['license_plate']).exists():
            vehicle = Vehicle.objects.create(**v_data)
            print(f"Created vehicle: {vehicle.name} ({vehicle.license_plate})")
        else:
            print(f"Vehicle with plate {v_data['license_plate']} already exists")


def create_sample_drivers():
    """Create sample drivers"""
    print("Creating sample drivers...")
    
    drivers_data = [
        {
            'first_name': 'John',
            'last_name': 'Smith',
            'email': 'john.smith@fleetflow.com',
            'phone': '+1-555-0101',
            'address': '123 Oak St, New York, NY 10001',
            'date_of_birth': '1980-05-15',
            'hire_date': '2022-01-15',
            'license_number': 'DL123456',
            'license_type': 'Commercial',
            'license_expiry': '2025-05-15',
            'status': 'on_duty',
            'emergency_contact': 'Jane Smith',
            'emergency_phone': '+1-555-0102',
            'salary': 45000.00
        },
        {
            'first_name': 'Maria',
            'last_name': 'Garcia',
            'email': 'maria.garcia@fleetflow.com',
            'phone': '+1-555-0203',
            'address': '456 Pine Ave, Los Angeles, CA 90001',
            'date_of_birth': '1985-08-22',
            'hire_date': '2021-06-10',
            'license_number': 'DL789012',
            'license_type': 'Commercial',
            'license_expiry': '2024-08-22',
            'status': 'on_duty',
            'emergency_contact': 'Carlos Garcia',
            'emergency_phone': '+1-555-0204',
            'salary': 48000.00
        },
        {
            'first_name': 'Robert',
            'last_name': 'Johnson',
            'email': 'robert.johnson@fleetflow.com',
            'phone': '+1-555-0305',
            'address': '789 Elm Rd, Chicago, IL 60007',
            'date_of_birth': '1978-12-03',
            'hire_date': '2020-03-20',
            'license_number': 'DL345678',
            'license_type': 'Heavy Vehicle',
            'license_expiry': '2025-12-03',
            'status': 'off_duty',
            'emergency_contact': 'Linda Johnson',
            'emergency_phone': '+1-555-0306',
            'salary': 52000.00
        }
    ]
    
    for d_data in drivers_data:
        if not Driver.objects.filter(license_number=d_data['license_number']).exists():
            driver = Driver.objects.create(**d_data)
            print(f"Created driver: {driver.full_name}")
        else:
            print(f"Driver with license {d_data['license_number']} already exists")


def main():
    """Main setup function"""
    print("FleetFlow Database Setup")
    print("=" * 50)
    
    try:
        create_initial_users()
        print()
        create_vehicle_types()
        print()
        create_maintenance_types()
        print()
        create_fuel_stations()
        print()
        create_sample_vehicles()
        print()
        create_sample_drivers()
        print()
        print("=" * 50)
        print("Database setup completed successfully!")
        print("\nDemo Credentials:")
        print("- Admin: admin / admin123")
        print("- Manager: manager / manager123")
        print("- Dispatcher: dispatcher / dispatch123")
        print("- Safety Officer: safety / safety123")
        print("- Financial Analyst: analyst / analyst123")
        
    except Exception as e:
        print(f"Error during setup: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
