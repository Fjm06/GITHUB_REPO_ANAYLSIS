# 🚀 Streamlit Cloud Deployment Guide

## Step 1: Prepare Your Repository

✅ **Already Done!**
- Code pushed to: https://github.com/Fjm06/GITHUB_REPO_ANAYLSIS
- .gitignore configured (excludes .env)
- requirements.txt updated

## Step 2: Deploy to Streamlit Cloud

### 2.1 Go to Streamlit Cloud
1. Visit: https://share.streamlit.io
2. Click "Sign in" (use your GitHub account)
3. Authorize Streamlit to access your GitHub

### 2.2 Create New App
1. Click "New app" button
2. Fill in the details:
   - **Repository:** `Fjm06/GITHUB_REPO_ANAYLSIS`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
   - **App URL:** Choose a custom URL (e.g., `github-repo-analyzer`)

### 2.3 Add Secrets (IMPORTANT!)
Before deploying, click "Advanced settings" → "Secrets"

Add your credentials in TOML format:

```toml
HUGGINGFACEHUB_API_TOKEN = "your_huggingface_token_here"
PINECONE_API_KEY = "your_pinecone_api_key_here"
GITHUB_TOKEN = "your_github_token_here"
```

**Note:** Use your actual tokens from .env file

### 2.4 Deploy
1. Click "Deploy!"
2. Wait 2-3 minutes for deployment
3. Your app will be live at: `https://your-app-name.streamlit.app`

## Step 3: Verify Deployment

Once deployed, check:
- ✅ Pinecone connection status (green indicator in sidebar)
- ✅ Add a test repository
- ✅ Chat functionality works
- ✅ Update and delete buttons work

## Troubleshooting

### Issue: "Module not found"
**Solution:** Check requirements.txt has all dependencies

### Issue: "Pinecone connection failed"
**Solution:** 
1. Verify API key in Streamlit secrets
2. Check Pinecone index exists (run setup_pinecone.py locally first)

### Issue: "HuggingFace API error"
**Solution:** 
1. Verify HuggingFace token in secrets
2. Check token has proper permissions

### Issue: "Out of memory"
**Solution:** Streamlit Cloud has memory limits. Consider:
- Using smaller embedding models
- Limiting chunk size
- Processing fewer files at once

## Step 4: Share Your App

Once deployed, share your app URL:
- `https://your-app-name.streamlit.app`

## Optional: Custom Domain

1. Go to app settings in Streamlit Cloud
2. Click "Custom domain"
3. Follow instructions to add your domain

## Monitoring

- View logs in Streamlit Cloud dashboard
- Check app health and usage statistics
- Monitor Pinecone usage in Pinecone dashboard

## Updating Your App

To update after deployment:
```bash
git add .
git commit -m "Update message"
git push origin main
```

Streamlit Cloud will automatically redeploy!

## Cost Considerations

**Free Tier Includes:**
- Streamlit Cloud: 1 private app, unlimited public apps
- Pinecone: 1 index, 100K vectors
- HuggingFace: Free API access (rate limited)

**Upgrade if needed:**
- Streamlit Cloud: $20/month for more apps
- Pinecone: $70/month for more indexes/vectors
- HuggingFace: Pro for faster inference

## Support

If you encounter issues:
1. Check Streamlit Cloud logs
2. Review GitHub Issues
3. Contact support@streamlit.io

---

**Your app is ready to deploy! 🎉**

Repository: https://github.com/Fjm06/GITHUB_REPO_ANAYLSIS
