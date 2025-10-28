# N5 OS Waitlist Setup Instructions

## Your website is live! 🎉

**URL:** https://n5-waitlist-va.zocomputer.io

## Next Steps: Add Your LaunchList Widget

### 1. Get Your LaunchList Form Key

1. Go to [LaunchList](https://getlaunchlist.com) and create an account
2. Create a new waitlist
3. Navigate to the **Integration** page from the sidebar
4. Copy your **form key** (it will look something like `ABC123XYZ`)

### 2. Add the Form Key to Your Website

Open `file 'n5-waitlist/src/index.tsx'` and find this line (around line 19):

```html
<!-- LaunchList Widget Script - ADD YOUR SCRIPT HERE -->
```

The script is already there. Now scroll down to find this line (around line 348):

```html
<div class="launchlist-widget" data-key-id="YOUR_FORM_KEY_HERE" data-height="180px">
```

Replace `YOUR_FORM_KEY_HERE` with your actual form key from LaunchList.

### 3. The Widget Will Auto-Load

Once you add your form key and save the file, the LaunchList widget will automatically replace the placeholder on your website!

## Customization Options

### Change Widget Height

In the same line, you can adjust the height:
```html
data-height="180px"  <!-- Change this value -->
```

### Customize LaunchList Settings

In your LaunchList dashboard, you can customize:
- Form fields (name, email, custom fields)
- Thank you page
- Email notifications
- Referral rewards
- And much more!

## Website Features

Your N5 OS waitlist website includes:

✅ N5 OS branding with rust/gold color scheme  
✅ Hero section with logo  
✅ LaunchList widget integration  
✅ Your testimonial from zo.computer  
✅ All 10 N5 OS capabilities explained  
✅ Comprehensive FAQ section  
✅ LinkedIn follow CTA  
✅ Zo promo link (50% off with VATT50)  
✅ Fully responsive design  
✅ Professional styling

## Support

If you need help:
- [LaunchList Documentation](https://getlaunchlist.com/help/docs)
- [LaunchList Integration Guide](https://getlaunchlist.com/help/docs/widget/integrate-widget)
- LaunchList Support: Live chat or email

## File Structure

```
n5-waitlist/
├── src/
│   └── index.tsx          # Main website file (edit this)
├── public/
│   └── n5-logo.jpg        # N5 OS logo
├── package.json
└── SETUP.md              # This file
```

---

**Built on Zo Computer** | **Powered by Hono + Bun**
