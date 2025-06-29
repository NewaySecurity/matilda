# MATILDA Deployment Guide
## Publishing to www.matilda.acorn

### Prerequisites
- GitHub account
- Domain registrar account (for .acorn domain)
- Netlify account (for hosting)

## Step 1: Domain Registration

### For .acorn Domain Registration:
1. **Check Domain Availability**:
   - Visit your preferred domain registrar (GoDaddy, Namecheap, Google Domains, etc.)
   - Search for "matilda.acorn"
   - Note: .acorn is a newer TLD, ensure your registrar supports it

2. **Alternative Domains** (if .acorn is not available):
   - matilda.ai
   - matilda.dev
   - matilda.io
   - matilda.tech
   - getmatilda.com

### Recommended Domain Registrars:
- **Namecheap** - Good pricing and management tools
- **Google Domains** - Excellent integration with Google services
- **Cloudflare Registrar** - Best pricing at cost
- **GoDaddy** - Widely supported

## Step 2: Setup Git Repository

```bash
# Initialize git repository (run in MATILDA directory)
git init
git add .
git commit -m "Initial MATILDA commit"

# Create GitHub repository
# Go to github.com and create new repository named "MATILDA"

# Add remote and push
git remote add origin https://github.com/yourusername/MATILDA.git
git branch -M main
git push -u origin main
```

## Step 3: Deploy to Netlify

### Option A: GitHub Integration (Recommended)
1. Sign up/login to [Netlify](https://netlify.com)
2. Click "New site from Git"
3. Connect your GitHub account
4. Select your MATILDA repository
5. Build settings:
   - Build command: `cd frontend && npm run build`
   - Publish directory: `frontend/build`
6. Click "Deploy site"

### Option B: Manual Deployment
1. Go to [Netlify](https://netlify.com)
2. Drag and drop your `frontend/build` folder
3. Netlify will provide a random URL

## Step 4: Configure Custom Domain

### In Netlify Dashboard:
1. Go to Site settings → Domain management
2. Click "Add custom domain"
3. Enter: `www.matilda.acorn`
4. Netlify will provide DNS settings

### Configure DNS (at your domain registrar):
Add these DNS records:

```
Type: CNAME
Name: www
Value: [your-netlify-subdomain].netlify.app

Type: A (for apex domain matilda.acorn)
Name: @
Value: 75.2.60.5 (Netlify's load balancer)

Type: AAAA (IPv6, optional)
Name: @
Value: 2600:1f14:e22:3300::1
```

## Step 5: SSL Certificate
- Netlify automatically provides SSL certificates
- Once DNS propagates (24-48 hours), your site will be accessible via HTTPS

## Step 6: Environment Variables

### In Netlify Dashboard:
1. Go to Site settings → Environment variables
2. Add these variables:
   ```
   REACT_APP_API_URL=https://api.matilda.acorn
   REACT_APP_ENVIRONMENT=production
   REACT_APP_SITE_URL=https://www.matilda.acorn
   ```

## Step 7: Backend Deployment (if needed)

### Options for Backend Hosting:
1. **Railway** - Easy deployment for Node.js/Python apps
2. **Heroku** - Popular platform-as-a-service
3. **DigitalOcean App Platform** - Simple container deployment
4. **AWS Lambda** - Serverless functions
5. **Vercel** - Great for Next.js/Node.js apps

### Backend Domain Setup:
- Deploy backend to chosen platform
- Configure subdomain: `api.matilda.acorn`
- Update DNS with CNAME pointing to your backend service

## Step 8: Testing

### Verify deployment:
1. Visit https://www.matilda.acorn
2. Test all functionality
3. Check mobile responsiveness
4. Verify API connections work

### Tools for testing:
- [GTmetrix](https://gtmetrix.com) - Performance testing
- [SSL Labs](https://ssllabs.com/ssltest/) - SSL configuration test
- [Google PageSpeed Insights](https://pagespeed.web.dev) - Performance audit

## Step 9: Monitoring & Analytics

### Recommended tools:
1. **Google Analytics** - User behavior tracking
2. **Netlify Analytics** - Built-in traffic analytics
3. **Uptime Robot** - Monitor site availability
4. **Sentry** - Error tracking and monitoring

## Costs Estimate

### Annual Costs:
- Domain (.acorn): $20-50/year
- Netlify Pro (optional): $19/month
- Backend hosting: $5-25/month
- **Total**: ~$100-400/year

### Free Tier Options:
- Netlify: Free for personal projects
- Railway: $5/month free credit
- Vercel: Free for hobby projects

## Security Considerations

1. **HTTPS Everywhere**: Ensure all connections use SSL
2. **Content Security Policy**: Add CSP headers
3. **Environment Variables**: Never commit API keys
4. **CORS Configuration**: Properly configure API endpoints
5. **Regular Updates**: Keep dependencies updated

## Troubleshooting

### Common Issues:
1. **DNS propagation delays**: Can take 24-48 hours
2. **SSL certificate issues**: Usually resolve automatically
3. **Build failures**: Check Node.js version compatibility
4. **API connection errors**: Verify environment variables

### Support Resources:
- Netlify Support: https://support.netlify.com
- DNS checker: https://dnschecker.org
- SSL checker: https://ssllabs.com/ssltest/

## Next Steps After Deployment

1. Set up monitoring and analytics
2. Configure automated backups
3. Implement SEO optimizations
4. Set up social media integration
5. Create documentation and user guides

---

**Ready to Deploy!** 
Your MATILDA application is now configured for production deployment at www.matilda.acorn!
