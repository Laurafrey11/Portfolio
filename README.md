# Portfolio
💡 About Me

I have a degree in Psychology and am a Data Analyst, with experience in education, data analysis, project management, and technology. Throughout my career, I have combined a human approach with analytics and innovation, participating in projects ranging from data visualization and BI to mentoring and training in digital tools.

I am passionate about the intersection of people, data, and technology: how information can improve processes, decisions, and experiences. I have worked in academic, corporate, and public environments, driving digital transformation processes, designing interactive dashboards, and training in Power BI, Tableau, Looker, Power Platform, and Fabric.

Currently, I continue my training in cloud services, automation, and low-code, seeking to integrate data analysis, UX, and organizational strategy to generate impact and sustainable value.

🔧 Specialties

📊 Data Analytics | Business Intelligence | Power BI | Tableau | Looker | Python | SQL

🤖 Power Platform | Automations | Azure | Google Cloud | N8N | AI

🧠 Organizational Psychology | Training | Talent Management

🎓 Education | Mentoring | Digital Skills Development

🎯 Interests

Digital transformation, educational innovation, analytics applied to human behavior, BI, and data-driven culture.

# 💡 Repository

## 📊 Power BI Dashboards

### 📈 HR Dashboard
![HR Dashboard](https://github.com/LauraFrey11/Portfolio/blob/main/HRDashboard.jpg)
![HR Dashboard](https://github.com/Laurafrey11/Portfolio/blob/main/HRDashboard2.jpg)
![HR Dashboard](https://github.com/LauraFrey11/Portfolio/blob/main/HRDashboard3.jpg)

Shows metrics on active HR and overall performance.
**Tech:** Power BI

### 💼 Marketing Dashboard
![Marketing Dashboard](https://github.com/LauraFrey11/Portfolio/blob/main/MarketingDashboard.jpg)
![Marketing Dashboard](https://github.com/Laurafrey11/Portfolio/blob/main/MarketingDashboard2.jpg)
![Marketing Dashboard](https://github.com/LauraFrey11/Portfolio/blob/main/MarketingDashboard3.jpg)
![Marketing Dashboard](https://github.com/LauraFrey11/Portfolio/blob/main/MarketingDashboard4.jpg)

Dynamic sales and customer report connected to real-time databases.
**Tech:** Power BI

---

## 📊 Looker Dashboard

### 📈 Marketing Dashboard
![looker2](https://github.com/Laurafrey11/Portfolio/blob/main/looker2.jpg)

Shows metrics on Marketing and overall performance.
**Tech:** Looker 

---

## 🤖 Artificial Intelligence

### 🧩 AI Customer Service Assistant for IG
![AI Assistant](https://github.com/LauraFrey11/Portfolio/blob/main/IG%20Chatwoot.jpg)

An agent who answers customer questions using AI in your Instagram DMs.
**Tech:** n8n + OpenAI + Instagram

### 🧠 Smart Sales Assistant
![AI Assistant](https://github.com/LauraFrey11/Portfolio/blob/main/Agente%20de%20Ventas.jpg)

An agent who answers customer questions using AI, selling products and saving the data in your CRM.
**Tech:** n8n + OpenAI + CRM

---

## 🔄 Automations

### ⚙️ Proposal Generator
![AI Assistant](https://github.com/LauraFrey11/Portfolio/blob/main/Mails%20template%20flow.jpg)

An agent who automatize email campaings. 
**Tech:** n8n + HTML 

### 🧾​ Pdf to Sheet
![pdf to sheet](https://github.com/LauraFrey11/Portfolio/blob/main/pdf%20to%20sheet.jpg)

An agent who reads invoices, transfers them to a document, and moves them to a processed folder.
**Tech:** n8n + PDF + Google + Open AI 

### 💻​ App Script Sheet
![App Script Sheet](https://github.com/LauraFrey11/Portfolio/blob/main/App%20Script%20Sheet.jpg)

Clean up data.
**Tech:** Google Sheet

### 💻​ SQL Procedure
USE YourDatabaseName;
GO

CREATE OR ALTER PROCEDURE sp_GetMonthlySalesGrowthByCategory
    @Year INT
AS
BEGIN
    SET NOCOUNT ON;

    /*
    =============================================================
     Author: Laura
     Project: SQL Portfolio – Sales Analytics
     Date: 2025-10-21

     Description:
        This stored procedure returns monthly total sales by
        category and calculates the percentage growth compared
        to the previous month.

     Parameters:
        @Year INT – The year to analyze.

     Output Columns:
        - Category               (VARCHAR)
        - Month                  (YYYY-MM)
        - TotalSales             (DECIMAL)
        - GrowthPercent          (% change from previous month)

     Formula:
        ((CurrentMonth - PreviousMonth) / PreviousMonth) * 100
    =============================================================
    */

    ;WITH MonthlySales AS (
        SELECT 
            c.CategoryName AS Category,
            FORMAT(v.SaleDate, 'yyyy-MM') AS [Month],
            SUM(v.Quantity * p.Price) AS TotalSales
        FROM Sales v
        INNER JOIN Products p ON v.ProductID = p.ProductID
        INNER JOIN Categories c ON p.CategoryID = c.CategoryID
        WHERE YEAR(v.SaleDate) = @Year
        GROUP BY c.CategoryName, FORMAT(v.SaleDate, 'yyyy-MM')
    )
    SELECT 
        Category,
        [Month],
        TotalSales,
        ROUND(
            CASE 
                WHEN LAG(TotalSales) OVER (PARTITION BY Category ORDER BY [Month]) = 0 
                    THEN NULL
                ELSE 
                    ((TotalSales - LAG(TotalSales) OVER (PARTITION BY Category ORDER BY [Month])) 
                    / LAG(TotalSales) OVER (PARTITION BY Category ORDER BY [Month])) * 100
            END, 2
        ) AS GrowthPercent
    FROM MonthlySales
    ORDER BY Category, [Month];

END;
GO
