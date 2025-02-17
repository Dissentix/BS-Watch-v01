# BS-Watch

# Comprehensive Reconnaissance for Bug Bounty Hunters  

This project is developed by Dissentix and the Believe Sec team to streamline and enhance the reconnaissance process for bug bounty hunting.  

## 🚀 Features  
- Efficient and automated reconnaissance  
- Helps bug bounty hunters gather **fresh assets**  
- Performs subdomain discovery, DNS resolution, and HTTP discovery  
- Sends fresh online assets to your Discord channel  

## 🎯 Get Started  
Clone the repository and start using Dissentix to level up your recon game!  

```bash
git clone https://github.com/Dissentix/BS-Watch-v01.git
```

## 🔥 How It Works  
1. **Subdomain Discovery:** BS-Watch starts by discovering subdomains for the given target.  
2. **DNS Resolution:** The discovered subdomains are then resolved to identify active assets.  
3. **HTTP Discovery:** Finally, BS-Watch performs HTTP discovery to identify live services.  
4. **Fresh Assets:** All fresh assets found online are then sent directly to your Discord channel.  

## ⭐️ Support Me!  
If you find this project useful, please consider **starring the repository**! Your support helps me continue building valuable tools for the security community. ðŸš€

## 🤝 Contribute  
Your feedback and suggestions are invaluable!  
Feel free to open issues or submit pull requests to improve the project.  

## Example Discord Output  
An example of the output you will receive in your Discord channel, in sequence:

---

🕰 **Current time in Iran:** 2025-01-24 03:19:22  

---

✉️ **Started sending URLs** from `/root/BS-Watch/sub-discovery/mytrainpal.com.httpx`.  

---

**URL:** [http://lepanierfrancais.com](http://lepanierfrancais.com)  
**Status:** [301, 200]  
**Details:** [French]  
**Providers:** Gourmet Market | France Delicacies | Luxury French Online | Le Panier Francais [https://lepanierfrancais.com](https://lepanierfrancais.com) | [Algolia, Cloudflare, Cloudflare Bot Management, HTTP/3, Klaviyo, Sanity, Shopify]  

💾 **(Fresh Asset)** has been added to 'trip' program DB  

---

**Finished sending URLs** from `/root/BS-Watch/sub-discovery/trip.com.httpx`.  
**Total URLs sent:** 472  
- **Status [403]:** 18  
- **Status [200]:** 16  
- **Status [521]:** 1  
- **Status [404]:** 11  
- **Status [409]:** 15  
- **Status [302,200]:** 20  
- **Status [301]:** 21  
- **Status [302]:** 1  
- **Status [525]:** 1  
- **Status [302,302,302]:** 18  
- **Status [301,200]:** 2  
- **Status [303,303,303]:** 1  
- **Status [502]:** 1  

---

**All new URLs have been successfully sent to Discord.**  
**Total URLs sent:** 126  

Happy Hunting! 🎉
