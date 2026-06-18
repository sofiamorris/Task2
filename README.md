# Hydrogen-Based DERMS for Renewable Energy Storage

## Overview

This project explores the use of hydrogen production, storage, and fuel cell technologies within a Distributed Energy Resource Management System (DERMS) to address renewable energy intermittency. The system analyzes real-world energy generation, demand, and electricity pricing data to evaluate the economic and operational benefits of converting excess solar energy into hydrogen for later use.

In addition to software modeling, a bench-scale prototype was developed using Arduino microcontrollers, solar power, an electrolyzer, and a hydrogen fuel cell to demonstrate the core concepts of power firming and renewable energy storage.

## Project Goals

- Reduce reliance on non-renewable energy during periods of low solar generation
- Store excess solar energy as hydrogen
- Generate revenue through hydrogen sales
- Evaluate the economic impact of hydrogen storage using real-world energy market data
- Demonstrate DERMS concepts through a physical prototype

## Technologies Used

### Software
- Python
- Pandas
- Matplotlib
- REST APIs
- CSV Data Processing

### Data Sources
- U.S. Energy Information Administration (EIA) API
- Southwest Power Pool (SPP) WEIS Market Data

### Hardware
- Arduino Uno
- Solar Panel
- Hydrogen Electrolyzer
- Hydrogen Fuel Cell
- LCD Display
- Relay Modules
- Digital Potentiometers
- MOSFETs
- UART Communication

## Methodology

The software system collects:

- Solar generation data
- Energy demand data
- Locational Marginal Pricing (LMP) data

The algorithm:

1. Retrieves and merges data from EIA and SPP APIs
2. Identifies energy surplus and deficit periods
3. Converts excess solar energy into stored hydrogen
4. Converts stored hydrogen back into electricity during shortages
5. Calculates cost savings from avoided energy purchases
6. Estimates revenue generated from hydrogen sales

## Bench-Scale Prototype

A physical demonstration system was developed to simulate DERMS behavior under varying solar generation conditions.

The system automatically:

- Supplies power directly from solar when available
- Utilizes stored energy when solar production is insufficient
- Directs excess energy to hydrogen production
- Maintains consistent power delivery despite changing inputs

## Results

### El Paso Electric (Residential)

- $2.6 million annual reduction in energy outsourcing costs
- Approximately $22 million annual hydrogen sales revenue

### Imperial Irrigation District (Utility Scale)

- $133 million annual hydrogen sales revenue
- Reduced dependence on imported energy during demand peaks

## Key Skills Demonstrated

- Energy Systems Modeling
- Data Engineering
- API Integration
- Time-Series Data Analysis
- Python Development
- Embedded Systems
- Arduino Programming
- Hardware-Software Integration
- Renewable Energy Technologies
- Technical Research

## Paper

The full project report can be found in:

`Sustainable Grid Stabilization.pdf`

## Authors

Senior Design Project  
California Polytechnic State University
