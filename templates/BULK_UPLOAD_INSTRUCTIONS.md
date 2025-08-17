# 🎬 Movie Bulk Upload Template Instructions

## 📋 Overview
This template allows you to upload multiple movies at once using CSV or Excel files. The system supports both formats with the same data structure.

## 📁 Template Files
- `movie_bulk_upload_template.csv` - CSV format template
- `movie_bulk_upload_template.xlsx` - Excel format template

## 📊 Required Fields

### ✅ **Mandatory Fields**
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `title` | Text | Movie title (max 255 chars) | "The Matrix" |
| `genre` | Text | Movie genre (max 100 chars) | "Sci-Fi" |

### 📝 **Optional Fields**
| Field | Type | Description | Example | Valid Values |
|-------|------|-------------|---------|--------------|
| `release_date` | Date | Release date | "1999-03-31" | YYYY-MM-DD format |
| `duration_minutes` | Number | Movie duration in minutes | 136 | Positive integer |
| `description` | Text | Movie description | "A computer programmer discovers..." | Any text |
| `director` | Text | Director name(s) | "The Wachowskis" | max 255 chars |
| `rating` | Text | Movie rating | "R" | U, PG, PG-13, R, etc. |
| `language` | Text | Primary language | "English" | max 50 chars |
| `country` | Text | Country of origin | "USA" | max 100 chars |
| `poster_url` | URL | Poster image URL | "https://example.com/poster.jpg" | Valid URL |
| `trailer_url` | URL | Trailer video URL | "https://example.com/trailer.mp4" | Valid URL |
| `status` | Text | Movie status | "Ready" | Ready, Uploaded, In Progress, New, Failed, Processing |
| `imdb_id` | Text | IMDB ID | "tt0133093" | max 20 chars |
| `tmdb_id` | Text | TMDB ID | "603" | max 20 chars |
| `box_office_collection` | Number | Box office earnings in millions | 463.5 | Decimal number |
| `budget` | Number | Production budget in millions | 63 | Decimal number |

## 🔧 Data Format Guidelines

### 📅 **Date Format**
- Use `YYYY-MM-DD` format (e.g., `2024-12-25`)
- Leave empty if unknown

### 💰 **Financial Fields**
- Enter amounts in millions (e.g., 463.5 for $463.5M)
- Use decimal points for precise amounts
- Leave empty if unknown

### 🌐 **URLs**
- Must be valid HTTP/HTTPS URLs
- Poster URLs should point to image files (jpg, png, etc.)
- Trailer URLs should point to video files (mp4, etc.)

### 📊 **Status Values**
Valid status options:
- `New` - Newly added movie
- `Ready` - Ready for processing
- `In Progress` - Currently being processed
- `Uploaded` - Successfully uploaded
- `Processing` - Being processed by system
- `Failed` - Processing failed

## 📝 **CSV Guidelines**

### ✅ **Do's**
- Use double quotes for text containing commas: `"Director One, Director Two"`
- Ensure proper escaping of special characters
- Use UTF-8 encoding for international characters
- Keep header row exactly as shown in template

### ❌ **Don'ts**
- Don't use different date formats
- Don't include currency symbols in financial fields
- Don't leave mandatory fields empty
- Don't modify column headers

## 📊 **Excel Guidelines**

### ✅ **Do's**
- Use the "Movies" sheet for data
- Format date columns as Date type
- Format financial columns as Number type
- Keep all data in the same sheet

### ❌ **Don'ts**
- Don't add extra sheets with data
- Don't merge cells
- Don't use formulas in data cells
- Don't change column order

## 🚀 **Upload Process**

1. **Download Template**: Use provided CSV or Excel template
2. **Fill Data**: Add your movie data following the guidelines
3. **Validate**: Check all mandatory fields are filled
4. **Upload**: Use the bulk upload feature in the Movies section
5. **Review**: Check upload results and fix any errors

## ⚠️ **Common Errors & Solutions**

| Error | Cause | Solution |
|-------|-------|----------|
| "Missing title" | Empty title field | Fill in movie title |
| "Invalid date format" | Wrong date format | Use YYYY-MM-DD format |
| "Invalid status" | Wrong status value | Use only valid status values |
| "URL format error" | Invalid URL | Check URL format (http/https) |
| "Duplicate title" | Movie already exists | Use unique titles or update existing |

## 💡 **Tips for Success**

1. **Start Small**: Test with 2-3 movies first
2. **Validate Data**: Double-check all URLs and dates
3. **Use Examples**: Follow the sample data format exactly
4. **Check Encoding**: Save CSV files with UTF-8 encoding
5. **Backup Data**: Keep a copy of your original file

## 📞 **Support**

If you encounter issues:
1. Check this guide first
2. Validate your data format
3. Try uploading a smaller batch
4. Contact system administrator if problems persist

---

**Version**: 1.0  
**Last Updated**: 2025-01-17  
**Compatible Formats**: CSV, Excel (.xlsx)