# Open Food Facts

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]

Home Assistant custom integration for [Open Food Facts](https://world.openfoodfacts.org/), the open database of food products from around the world.

This integration does not expose entity platforms. Instead, it exposes powerful **service actions** that return structured data for use in Home Assistant automations, scripts, and template sensors.

## ✨ Features

- **Zero Configuration**: Single-click setup — no username, password, or API keys required.
- **Product Lookup**: Retrieve product details by barcode (EAN, UPC) via `open_food_facts.get_product`.
- **Product Search**: Search food products by keyword query via `open_food_facts.search_products`.
- **Rich Data**: Access product names, brands, ingredients, Nutri-Score, Eco-Score, NOVA groups, allergens, and nutrient levels.
- **Async & Non-Blocking**: Fully conforms to Home Assistant's async execution patterns using executor offloading.
- **Automation Ready**: Uses modern Home Assistant service response data (`SupportsResponse.ONLY`).

## 🚀 Quick Start

### Step 1: Install via HACS

1. In Home Assistant, open **HACS** → **Integrations**.
2. Search for **Open Food Facts** and click **Download**.
3. **Restart Home Assistant** after installation.

### Step 2: Add the Integration

1. Go to **Settings** → **Devices & Services**.
2. Click **Add Integration** and search for **Open Food Facts**.
3. Click **Submit** to confirm. Setup is complete!

## 🛠 Service Actions

### `open_food_facts.get_product`

Retrieves food product information for a given barcode.

#### Parameters

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `barcode` | String | Yes | Barcode (EAN, UPC) of the product (e.g. `"3017620422003"`). |
| `fields` | List | No | Optional list of specific fields to return (e.g. `["product_name", "nutriscore_grade"]`). |

#### Example Automation / Script

```yaml
action: open_food_facts.get_product
data:
  barcode: "3017620422003"
  fields:
    - product_name
    - brands
    - nutriscore_grade
    - ecoscore_grade
    - ingredients_text
response_variable: product_info
```

Response structure:
```json
{
  "product": {
    "code": "3017620422003",
    "product_name": "Nutella",
    "brands": "Ferrero",
    "nutriscore_grade": "e",
    "ecoscore_grade": "d"
  }
}
```

If the product barcode is not found in Open Food Facts, `product` is returned as `null`:
```json
{
  "product": null
}
```

---

### `open_food_facts.search_products`

Searches products by keyword.

#### Parameters

| Field | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `query` | String | Yes | — | Search query (e.g. `"sparkling water"`). |
| `page` | Integer | No | `1` | Page number (starting at 1). |
| `page_size` | Integer | No | `20` | Results per page (1–100). |
| `sort_by` | String | No | — | Sort order (e.g. `"product_name"`). |

#### Example Automation / Script

```yaml
action: open_food_facts.search_products
data:
  query: "sparkling water"
  page: 1
  page_size: 5
response_variable: search_results
```

Response structure:
```json
{
  "count": 420,
  "page": 1,
  "page_count": 5,
  "page_size": 5,
  "products": [
    {
      "code": "123456789",
      "product_name": "Natural Sparkling Mineral Water"
    }
  ]
}
```

---

## 🏷 Barcode Scanning Example

When using a barcode scanner or NFC/tag reader in Home Assistant:

```yaml
alias: "Barcode Scanned - Lookup Product"
trigger:
  - trigger: event
    event_type: tag_scanned
action:
  - action: open_food_facts.get_product
    data:
      barcode: "{{ trigger.event.data.tag_id }}"
    response_variable: off_result
  - choose:
      - conditions:
          - condition: template
            value_template: "{{ off_result.product is not none }}"
        sequence:
          - action: persistent_notification.create
            data:
              title: "Product Scanned"
              message: >
                Found: {{ off_result.product.product_name }}
                Nutri-Score: {{ off_result.product.nutriscore_grade | upper }}
```

## 📄 License

This integration is licensed under the Apache-2.0 License. Data is provided by [Open Food Facts](https://world.openfoodfacts.org/) under the Open Database License (ODbL).

[releases-shield]: https://img.shields.io/github/v/release/pantherale0/ha-openfoodfacts.svg?style=for-the-badge
[releases]: https://github.com/pantherale0/ha-openfoodfacts/releases
[commits-shield]: https://img.shields.io/github/commit-activity/y/pantherale0/ha-openfoodfacts.svg?style=for-the-badge
[commits]: https://github.com/pantherale0/ha-openfoodfacts/commits/main
[license-shield]: https://img.shields.io/github/license/pantherale0/ha-openfoodfacts.svg?style=for-the-badge
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40pantherale0-blue.svg?style=for-the-badge
