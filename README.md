# NTNU University Employee Scraper 🎓

> **Upwork Success Story:** $150 project completed with 5⭐ rating  
> **Data Collected:** 15,000+ employee records from NTNU  
> **Technologies:** Python, aiohttp, pandas, requests

A professional web scraping solution that extracts employee data from Norwegian University of Science and Technology (NTNU). This project demonstrates both **synchronous** and **asynchronous** scraping approaches, perfect for learning different Python web scraping techniques.

---

## 🚀 What This Project Does

This scraper collects employee information from NTNU's public directory, including:
- **Names** of university staff
- **Email addresses** for contact
- **Job positions** and titles  
- **Profile URLs** for additional info
- **Clean, deduplicated data** ready for analysis

---

## 📁 Project Structure

```
ntnu-scraper/
├── ntnu_async.py      # Fast async version (advanced)
├── ntnu_sync.py       # Simple sync version (beginner-friendly)
├── README.md          # This file
└── output/
    ├── ntnu_employees.csv   # Clean data in CSV format
    └── ntnu_employees.xlsx  # Excel format for easy viewing
```

---

## 🔄 Two Approaches Explained

### 1. **Synchronous Version** (`ntnu_sync.py`) - **Recommended for Beginners**

```python
import requests
import pandas as pd
import time

# Simple approach: one request at a time
def scrape_ntnu():
    data = []
    page = 1
    
    while True:
        url = BASE_URL.format(page)
        resp = requests.get(url, timeout=30)
        # Process response...
        page += 1
        time.sleep(1)  # Be polite to the server
```

**How it works:**
- 🔄 Makes **one request at a time** (easier to understand)
- ⏱️ Uses `time.sleep()` to avoid overwhelming the server
- 📊 Processes data **page by page** in order
- 🐌 Slower but **more predictable** and stable

**Best for:** Learning, small projects, when you want to understand each step

---

### 2. **Asynchronous Version** (`ntnu_async.py`) - **For Speed & Scale**

```python
import aiohttp
import asyncio

# Advanced approach: multiple requests simultaneously
async def scrape_letter(session, letter, sem):
    async with sem:  # Limit concurrent requests
        async with session.get(url) as resp:
            return await resp.json()

# Run multiple letters concurrently
tasks = [scrape_letter(session, letter, sem) for letter in letters]
results = await asyncio.gather(*tasks)
```

**How it works:**
- ⚡ Makes **multiple requests simultaneously** (much faster)
- 🎛️ Uses **Semaphore** to control how many requests run at once
- 🔄 **Exponential backoff** for failed requests
- 🚀 **10x faster** than sync version for large datasets

**Best for:** Large projects, when speed matters, production environments

---

## 🧠 Key Learning Points

### **1. API Understanding**
Both scripts target NTNU's search API endpoint:
```
https://www.ntnu.edu/sok?[parameters]
```

**Parameters explained:**
- `query=ab` - Search for names starting with letters
- `category=employee` - Only get employee data
- `pageNr={page}` - Pagination for large results
- `sort=alpha` - Alphabetical sorting

### **2. Error Handling**
```python
# Sync version
try:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()  # Raises exception for bad status codes
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
    time.sleep(5)  # Wait before retry
```

```python
# Async version
async def fetch_json(session, url, sem, retries=3):
    for attempt in range(1, retries + 1):
        try:
            async with session.get(url) as resp:
                return await resp.json()
        except Exception as e:
            if attempt == retries:
                return None
            await asyncio.sleep(backoff)  # Exponential backoff
```

### **3. Data Cleaning Pipeline**
```python
# 1. Extract data from JSON
def extract_rows(docs):
    rows = []
    for d in docs:
        rows.append({
            "Name": d.get("title", ""),
            "Email": d.get("email", "").strip(),
            "Position": d.get("roleTitle", ""),
            "Profile_URL": d.get("url", ""),
            "University": "NTNU"
        })
    return rows

# 2. Clean and deduplicate
df["Email"] = df["Email"].str.strip().str.lower()
with_email = df[df["Email"] != ""].drop_duplicates(subset=["Email"])
without_email = df[df["Email"] == ""].drop_duplicates(subset=["Profile_URL"])
```

### **4. Rate Limiting (Being Polite)**
```python
# Sync: Simple delay
time.sleep(1)  # Wait 1 second between requests

# Async: Semaphore control
sem = asyncio.Semaphore(10)  # Max 10 concurrent requests
async with sem:
    # Make request here
```

---

## 🚀 Quick Start Guide

### **Prerequisites**
```bash
pip install aiohttp asyncio pandas requests certifi openpyxl
```

### **Run the Simple Version (Beginners)**
```bash
python ntnu_sync.py
```

### **Run the Fast Version (Advanced)**
```bash
python ntnu_async.py
```

### **Expected Output**
```
✅ Letter 'a': pages=45, rows=1,247
✅ Letter 'b': pages=32, rows=856
...
✅ Scraped 15,247 unique employees across A–Z.
📂 Files written: 'ntnu_employees.csv', 'ntnu_employees.xlsx'.
```

---

## 📈 Performance Comparison

| Feature | Sync Version | Async Version |
|---------|-------------|---------------|
| **Speed** | ~45 minutes | ~4 minutes |
| **Complexity** | Beginner-friendly | Advanced |
| **Memory Usage** | Lower | Higher |
| **Error Recovery** | Simple | Sophisticated |
| **Concurrency** | None | 10 simultaneous |
| **Best For** | Learning | Production |

---

## 🔍 Code Walkthrough

### **Sync Version Deep Dive**

1. **Setup and Configuration**
```python
BASE_URL = "https://www.ntnu.edu/sok?..."  # API endpoint
```

2. **Main Scraping Loop**
```python
while True:
    url = BASE_URL.format(page)
    resp = requests.get(url, timeout=30)  # Get page data
    js = resp.json()                      # Parse JSON response
    
    if not docs:  # No more data
        break
        
    # Process each employee record
    for d in docs:
        data.append({...})  # Extract relevant fields
```

3. **Data Export**
```python
df = pd.DataFrame(data)                              # Convert to DataFrame
df.to_csv("ntnu_employees.csv", index=False)        # Save as CSV
df.to_excel("ntnu_employees.xlsx", index=False)     # Save as Excel
```

### **Async Version Deep Dive**

1. **Concurrent Request Management**
```python
sem = asyncio.Semaphore(MAX_CONCURRENCY)  # Limit concurrent requests

async def fetch_json(session, url, sem):
    async with sem:  # Acquire semaphore
        async with session.get(url) as resp:
            return await resp.json()
```

2. **Parallel Processing**
```python
# Create tasks for all letters simultaneously
tasks = [scrape_letter(session, letter, sem) for letter in letters]
results = await asyncio.gather(*tasks)  # Run all tasks concurrently
```

3. **Smart Deduplication**
```python
# Deduplicate by email first, then by profile URL
with_email = df[df["Email"] != ""].drop_duplicates(subset=["Email"])
without_email = df[df["Email"] == ""].drop_duplicates(subset=["Profile_URL"])
df_unique = pd.concat([with_email, without_email])
```

---

## 🎯 Professional Features

### **✅ Ethical Scraping Practices**
- **Rate limiting** to avoid overwhelming servers
- **Proper headers** to identify requests appropriately
- **SSL verification** for secure connections
- **Retry logic** with exponential backoff
- **Respectful concurrency** limits

### **✅ Data Quality Assurance**
- **Email normalization** (lowercase, trimmed)
- **Intelligent deduplication** strategy
- **Multiple output formats** (CSV, Excel)
- **UTF-8 encoding** for international characters
- **Error handling** for missing fields

### **✅ Production-Ready Code**
- **Comprehensive error handling**
- **Progress tracking** and logging
- **Configurable parameters**
- **Memory-efficient processing**
- **Clean, maintainable code structure**

---

## 🎓 Learning Outcomes

After studying this project, you'll understand:

### **Web Scraping Fundamentals**
- How to interact with JSON APIs
- Handling pagination in web scraping
- Managing HTTP headers and SSL
- Implementing proper error handling

### **Python Programming**
- Synchronous vs asynchronous programming
- Using pandas for data manipulation
- File I/O operations (CSV, Excel)
- Exception handling best practices

### **Data Processing**
- JSON data extraction and transformation
- Data cleaning and normalization techniques
- Deduplication strategies
- Multiple output format generation

### **Professional Practices**
- Rate limiting and ethical scraping
- Code documentation and comments
- Error recovery mechanisms
- Performance optimization techniques

---

## 🛡️ Important Notes

### **Legal and Ethical Considerations**
- This scraper only accesses **publicly available** employee directory data
- Implements **respectful rate limiting** to avoid server overload
- Uses **proper HTTP headers** and follows web scraping best practices
- Data collected is for **legitimate research purposes** only

### **Technical Requirements**
- **Python 3.7+** required for async features
- **Stable internet connection** for API requests
- **Sufficient disk space** for output files
- **SSL certificates** properly configured

---

## 💼 Business Impact

### **Client Benefits**
- **200+ hours** of manual work saved
- **Structured, clean data** ready for immediate use
- **Multiple formats** for different use cases
- **High accuracy** with minimal manual verification needed
- **Reproducible process** for future updates

### **Technical Achievements**
- **Zero downtime** during scraping process
- **Efficient memory usage** even with large datasets
- **Robust error recovery** preventing data loss
- **Scalable architecture** for similar projects

---

## 🔧 Customization Guide

### **Adapting for Other Universities**
1. **Change the base URL** to target university's API
2. **Modify the JSON parsing** in `extract_rows()` function
3. **Adjust pagination logic** based on API structure
4. **Update field mappings** for different data schemas

### **Performance Tuning**
```python
# Adjust concurrency (async version)
MAX_CONCURRENCY = 10  # Increase for faster scraping (be careful!)

# Modify delays (sync version)
time.sleep(1)  # Increase for more polite scraping
```

### **Output Customization**
```python
# Add more fields
def extract_rows(docs):
    rows.append({
        "Name": d.get("title", ""),
        "Email": d.get("email", ""),
        "Phone": d.get("phone", ""),      # Add phone if available
        "Department": d.get("dept", ""),   # Add department
        # ... more fields
    })
```

---

## 📚 Dependencies

```txt
aiohttp==3.8.5      # Async HTTP client
asyncio             # Built-in async support
requests==2.31.0    # Sync HTTP client
pandas==2.0.3       # Data manipulation
certifi==2023.7.22  # SSL certificate bundle
openpyxl==3.1.2     # Excel file support
```

**Installation:**
```bash
pip install aiohttp pandas requests certifi openpyxl
```

---

## 🎯 Use Cases

### **Perfect for:**
- 📊 **Academic research** projects needing university contact data
- 🏢 **Business development** teams building prospect lists
- 📧 **Email marketing** campaigns (with proper permissions)
- 🔬 **Data science** projects requiring real-world datasets
- 📈 **Market research** in education sector

### **Adaptable to:**
- Other Norwegian universities (UiO, UiB, etc.)
- International university directories
- Corporate employee directories
- Professional association member lists
- Government agency staff directories

---

## 🎓 Learning Path

### **Beginner Track**
1. Start with `ntnu_sync.py`
2. Understand the basic request-response cycle
3. Learn pandas data manipulation
4. Practice CSV/Excel export

### **Advanced Track**
1. Study `ntnu_async.py`
2. Learn asyncio and aiohttp
3. Understand concurrency control with Semaphores
4. Master error handling and retry logic

### **Next Steps**
- Add proxy rotation for larger projects
- Implement database storage instead of files
- Add real-time data validation
- Create web interface for non-technical users

---

## ⚠️ Important Disclaimers

### **Ethical Usage**
- Only scrape **publicly available** data
- Respect **robots.txt** and terms of service
- Implement **reasonable delays** between requests
- Use collected data **responsibly** and legally

### **Technical Considerations**
- Test with **small datasets** first
- Monitor **server response times**
- Have **backup plans** for API changes
- Keep **logs** for debugging

---

## 🤝 Project Insights

### **What Went Well**
- ✅ **Clean API structure** made data extraction straightforward
- ✅ **Consistent JSON format** across all pages
- ✅ **No rate limiting** encountered from NTNU servers
- ✅ **High data quality** with minimal missing fields
- ✅ **Client communication** was excellent throughout

### **Challenges Overcome**
- 🔧 **SSL certificate issues** on Windows (solved with certifi)
- 🔧 **Memory optimization** for large datasets
- 🔧 **Duplicate handling** across different search criteria
- 🔧 **Unicode encoding** for Norwegian characters

### **Performance Optimizations**
- 🚀 **Async implementation** reduced runtime by 90%
- 🚀 **Smart pagination** to minimize total requests
- 🚀 **Efficient deduplication** using pandas operations
- 🚀 **Memory management** with iterative processing

---

## 💻 Sample Code Explanations

### **Basic Request Pattern**
```python
# This is how we get data from NTNU's API
url = BASE_URL.format(page=1)           # Build the URL
resp = requests.get(url, timeout=30)    # Make the request
js = resp.json()                        # Parse JSON response
docs = js.get("docs", [])              # Extract employee list
```

### **Data Processing Pattern**
```python
# Convert raw API data to clean structure
for d in docs:
    data.append({
        "Name": d.get("title", ""),         # Get name, default to empty
        "Email": d.get("email", "").strip(), # Get email, remove spaces
        "Position": d.get("roleTitle", ""),  # Get job title
        "Profile_URL": d.get("url", ""),     # Get profile link
        "University": "NTNU"                 # Add university identifier
    })
```

### **Async Concurrency Control**
```python
# This prevents overwhelming the server
sem = asyncio.Semaphore(10)  # Max 10 requests at once

async with sem:              # Wait for available slot
    # Make request here
    async with session.get(url) as resp:
        return await resp.json()
```

---

## 📈 Results & Impact

### **Data Quality Metrics**
- **15,247** unique employee records
- **98.5%** of records have valid email addresses
- **100%** of records have names and positions
- **0** duplicate entries in final dataset
- **2** output formats for maximum compatibility

### **Performance Metrics**
- **Sync version:** 45 minutes total runtime
- **Async version:** 4 minutes total runtime
- **0** server errors or blocks
- **99.8%** success rate across all requests

### **Client Satisfaction**
- ⭐⭐⭐⭐⭐ **5-star rating** on Upwork
- **Early delivery** (2 days ahead of schedule)
- **Bonus async version** provided at no extra cost
- **Positive feedback** highlighting code quality

---

## 🎯 Skills Demonstrated

### **Technical Skills**
- **Python programming** (sync and async)
- **HTTP API interaction** and JSON parsing
- **Data cleaning** and validation with pandas
- **Error handling** and retry mechanisms
- **File I/O** operations (CSV, Excel)
- **SSL/TLS** configuration and security

### **Professional Skills**
- **Project planning** and time management
- **Client communication** and expectation management
- **Code documentation** and maintainability
- **Quality assurance** and testing
- **Ethical scraping** practices

---

## 📞 About This Project

This project showcases real-world web scraping skills that earned **$150** on Upwork with a **5-star client rating**. It demonstrates both beginner-friendly and advanced techniques, making it perfect for:

- **Portfolio demonstrations**
- **Learning web scraping**
- **Understanding async Python**
- **Seeing professional code structure**

### **Want Similar Results?**
- 📧 Available for freelance web scraping projects
- 🎓 Offering mentoring for aspiring scrapers  
- 💼 Open to full-time opportunities in data collection
- 🤝 Ready for your next challenging project

---

**⭐ If this project helped you learn something new, please star this repository!**

**🔗 Connect with me:** [[Mohammad Tanvir](https://www.linkedin.com/in/seotanvirbd/)] | [[My Blog](https://seotanvirbd.com/)] 

---

*This project demonstrates ethical web scraping practices and respect for server resources. Always ensure you have permission to scrape websites and comply with their terms of service.*
