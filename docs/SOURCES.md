# Source Notes

## CMHC Rental Market Survey

CMHC publishes Rental Market Survey data tables covering average rents, vacancy rates, unit counts, and other rental market indicators. The project is designed around CMHC average rent tables by geography and bedroom type.

Useful starting points:

- CMHC Rental Market Data: https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/housing-data/data-tables/rental-market
- Average Apartment Rents (Vacant & Occupied Units): https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/housing-data/data-tables/rental-market/average-apartment-rents-vacant-occupied
- Rental Market Survey methodology: https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/housing-research/surveys/methods/methodology-rental-market-survey

## City of Toronto Open Data

Toronto Open Data provides boundary and neighbourhood context datasets. The ETL includes a discovery command for CKAN resources:

```bash
rent-heatmap discover-boundaries --query "neighbourhood boundary"
```

Useful starting points:

- Toronto Open Data: https://open.toronto.ca/
- Neighbourhood Profiles: https://open.toronto.ca/dataset/neighbourhood-profiles/

## Licensing Reminder

Before redistributing full CMHC source tables, review CMHC terms attached to the downloaded table. This repository ships only a small sample file for development.
