"""
Frontend asset optimization utilities.
"""

import os
import gzip
import hashlib
from flask import current_app, request, make_response
from functools import wraps
import mimetypes

class AssetOptimizer:
    """Handle frontend asset optimization."""
    
    @staticmethod
    def get_file_hash(filepath):
        """Generate hash for file versioning."""
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()[:8]
        except FileNotFoundError:
            return 'missing'
    
    @staticmethod
    def get_versioned_url(filename):
        """Get versioned URL for static files."""
        static_folder = current_app.static_folder
        filepath = os.path.join(static_folder, filename)
        
        if os.path.exists(filepath):
            file_hash = AssetOptimizer.get_file_hash(filepath)
            return f"/static/{filename}?v={file_hash}"
        
        return f"/static/{filename}"
    
    @staticmethod
    def compress_static_files():
        """Pre-compress static files for better performance."""
        static_folder = current_app.static_folder
        compressed_files = []
        
        # File types to compress
        compressible_extensions = ['.css', '.js', '.html', '.svg', '.json']
        
        for root, dirs, files in os.walk(static_folder):
            for file in files:
                filepath = os.path.join(root, file)
                _, ext = os.path.splitext(file)
                
                if ext.lower() in compressible_extensions:
                    gzip_path = filepath + '.gz'
                    
                    # Only compress if gzip file doesn't exist or is older
                    if (not os.path.exists(gzip_path) or 
                        os.path.getmtime(filepath) > os.path.getmtime(gzip_path)):
                        
                        try:
                            with open(filepath, 'rb') as f_in:
                                with gzip.open(gzip_path, 'wb') as f_out:
                                    f_out.writelines(f_in)
                            
                            compressed_files.append(gzip_path)
                            
                        except Exception as e:
                            current_app.logger.error(f"Error compressing {filepath}: {str(e)}")
        
        current_app.logger.info(f"Compressed {len(compressed_files)} static files")
        return compressed_files

def add_cache_headers(response, cache_timeout=31536000):  # 1 year default
    """Add caching headers to response."""
    response.headers['Cache-Control'] = f'public, max-age={cache_timeout}'
    response.headers['Expires'] = 'Thu, 31 Dec 2037 23:55:55 GMT'
    return response

def gzip_response(f):
    """Decorator to gzip compress responses."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        
        # Check if client accepts gzip
        if 'gzip' not in request.headers.get('Accept-Encoding', ''):
            return response
        
        # Only compress text-based content
        content_type = response.headers.get('Content-Type', '')
        compressible_types = [
            'text/html', 'text/css', 'text/javascript', 
            'application/javascript', 'application/json',
            'text/plain', 'application/xml', 'text/xml'
        ]
        
        if not any(ct in content_type for ct in compressible_types):
            return response
        
        # Don't compress if already compressed or too small
        if (response.headers.get('Content-Encoding') or 
            len(response.get_data()) < 1000):
            return response
        
        # Compress the response
        try:
            compressed_data = gzip.compress(response.get_data())
            response.set_data(compressed_data)
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = len(compressed_data)
        except Exception as e:
            current_app.logger.error(f"Error compressing response: {str(e)}")
        
        return response
    
    return decorated_function

class StaticFileHandler:
    """Enhanced static file handling with optimization."""
    
    @staticmethod
    def serve_optimized_static(filename):
        """Serve static files with optimization."""
        static_folder = current_app.static_folder
        filepath = os.path.join(static_folder, filename)
        
        if not os.path.exists(filepath):
            return None
        
        # Check for pre-compressed version
        gzip_path = filepath + '.gz'
        if (os.path.exists(gzip_path) and 
            'gzip' in request.headers.get('Accept-Encoding', '')):
            
            with open(gzip_path, 'rb') as f:
                content = f.read()
            
            response = make_response(content)
            response.headers['Content-Encoding'] = 'gzip'
        else:
            with open(filepath, 'rb') as f:
                content = f.read()
            response = make_response(content)
        
        # Set appropriate content type
        content_type, _ = mimetypes.guess_type(filename)
        if content_type:
            response.headers['Content-Type'] = content_type
        
        # Add caching headers for static assets
        if any(filename.endswith(ext) for ext in ['.css', '.js', '.png', '.jpg', '.gif', '.svg']):
            response = add_cache_headers(response)
        
        return response

def minify_css(css_content):
    """Basic CSS minification."""
    import re
    
    # Remove comments
    css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
    
    # Remove unnecessary whitespace
    css_content = re.sub(r'\s+', ' ', css_content)
    css_content = re.sub(r';\s*}', '}', css_content)
    css_content = re.sub(r'{\s*', '{', css_content)
    css_content = re.sub(r'}\s*', '}', css_content)
    css_content = re.sub(r':\s*', ':', css_content)
    css_content = re.sub(r';\s*', ';', css_content)
    
    return css_content.strip()

def minify_js(js_content):
    """Basic JavaScript minification."""
    import re
    
    # Remove single-line comments (but preserve URLs)
    js_content = re.sub(r'(?<!:)//.*$', '', js_content, flags=re.MULTILINE)
    
    # Remove multi-line comments
    js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
    
    # Remove unnecessary whitespace
    js_content = re.sub(r'\s+', ' ', js_content)
    js_content = re.sub(r';\s*', ';', js_content)
    js_content = re.sub(r'{\s*', '{', js_content)
    js_content = re.sub(r'}\s*', '}', js_content)
    
    return js_content.strip()

class AssetBundler:
    """Bundle and optimize CSS/JS assets."""
    
    def __init__(self):
        self.css_files = []
        self.js_files = []
    
    def add_css(self, filename):
        """Add CSS file to bundle."""
        self.css_files.append(filename)
    
    def add_js(self, filename):
        """Add JavaScript file to bundle."""
        self.js_files.append(filename)
    
    def bundle_css(self, output_filename='bundle.css'):
        """Bundle and minify CSS files."""
        static_folder = current_app.static_folder
        css_folder = os.path.join(static_folder, 'css')
        
        bundled_content = []
        
        for css_file in self.css_files:
            filepath = os.path.join(css_folder, css_file)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    minified = minify_css(content)
                    bundled_content.append(f"/* {css_file} */\n{minified}")
        
        # Write bundled file
        output_path = os.path.join(css_folder, output_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(bundled_content))
        
        # Create gzipped version
        with gzip.open(output_path + '.gz', 'wt', encoding='utf-8') as f:
            f.write('\n'.join(bundled_content))
        
        return output_filename
    
    def bundle_js(self, output_filename='bundle.js'):
        """Bundle and minify JavaScript files."""
        static_folder = current_app.static_folder
        js_folder = os.path.join(static_folder, 'js')
        
        bundled_content = []
        
        for js_file in self.js_files:
            filepath = os.path.join(js_folder, js_file)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    minified = minify_js(content)
                    bundled_content.append(f"/* {js_file} */\n{minified}")
        
        # Write bundled file
        output_path = os.path.join(js_folder, output_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(bundled_content))
        
        # Create gzipped version
        with gzip.open(output_path + '.gz', 'wt', encoding='utf-8') as f:
            f.write('\n'.join(bundled_content))
        
        return output_filename

def create_asset_manifest():
    """Create manifest file for asset versioning."""
    static_folder = current_app.static_folder
    manifest = {}
    
    # Scan CSS files
    css_folder = os.path.join(static_folder, 'css')
    if os.path.exists(css_folder):
        for file in os.listdir(css_folder):
            if file.endswith('.css'):
                filepath = os.path.join(css_folder, file)
                file_hash = AssetOptimizer.get_file_hash(filepath)
                manifest[f'css/{file}'] = f'css/{file}?v={file_hash}'
    
    # Scan JS files
    js_folder = os.path.join(static_folder, 'js')
    if os.path.exists(js_folder):
        for file in os.listdir(js_folder):
            if file.endswith('.js'):
                filepath = os.path.join(js_folder, file)
                file_hash = AssetOptimizer.get_file_hash(filepath)
                manifest[f'js/{file}'] = f'js/{file}?v={file_hash}'
    
    # Write manifest file
    manifest_path = os.path.join(static_folder, 'manifest.json')
    import json
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return manifest

# Template helper functions
def asset_url(filename):
    """Template helper to get versioned asset URL."""
    return AssetOptimizer.get_versioned_url(filename)

def critical_css():
    """Return critical CSS that should be inlined."""
    # This would contain the most important CSS for above-the-fold content
    return """
    /* Critical CSS - inline in head */
    body { font-family: system-ui, -apple-system, sans-serif; margin: 0; }
    .header { background: #55970f; color: white; padding: 1rem; }
    .loading { display: flex; justify-content: center; padding: 2rem; }
    .btn-primary { background: #55970f; color: white; padding: 0.5rem 1rem; border: none; border-radius: 4px; }
    """

class ResourceHints:
    """Generate resource hints for better performance."""
    
    @staticmethod
    def get_preload_links():
        """Get preload links for critical resources."""
        return [
            '<link rel="preload" href="/static/css/main.css" as="style">',
            '<link rel="preload" href="/static/js/main.js" as="script">',
            '<link rel="preload" href="/static/fonts/main.woff2" as="font" type="font/woff2" crossorigin>',
        ]
    
    @staticmethod
    def get_prefetch_links():
        """Get prefetch links for likely next resources."""
        return [
            '<link rel="prefetch" href="/static/js/analytics.js">',
            '<link rel="prefetch" href="/dashboard">',
            '<link rel="prefetch" href="/social/feed">',
        ]
    
    @staticmethod
    def get_dns_prefetch_links():
        """Get DNS prefetch links for external domains."""
        return [
            '<link rel="dns-prefetch" href="//fonts.googleapis.com">',
            '<link rel="dns-prefetch" href="//cdn.jsdelivr.net">',
        ]

class ImageOptimizer:
    """Optimize images for better performance."""
    
    @staticmethod
    def generate_responsive_image_html(src, alt, sizes=None):
        """Generate responsive image HTML with multiple sizes."""
        if sizes is None:
            sizes = [320, 640, 1024, 1920]
        
        # Generate srcset for different sizes
        srcset_parts = []
        for size in sizes:
            # In a real implementation, you'd have actual resized images
            srcset_parts.append(f"{src}?w={size} {size}w")
        
        srcset = ", ".join(srcset_parts)
        
        return f'''<img src="{src}" 
                       srcset="{srcset}" 
                       sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 25vw"
                       alt="{alt}" 
                       loading="lazy">'''
    
    @staticmethod
    def get_placeholder_svg(width=300, height=200, text="Loading..."):
        """Generate SVG placeholder for lazy loading."""
        return f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
                     <rect width="100%" height="100%" fill="#f0f0f0"/>
                     <text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="#999">{text}</text>
                   </svg>'''

class PerformanceOptimizer:
    """Comprehensive performance optimization utilities."""
    
    @staticmethod
    def optimize_html_response(html_content):
        """Optimize HTML response for better performance."""
        import re
        
        # Remove unnecessary whitespace
        html_content = re.sub(r'\s+', ' ', html_content)
        html_content = re.sub(r'>\s+<', '><', html_content)
        
        # Remove HTML comments (but preserve conditional comments)
        html_content = re.sub(r'<!--(?!\[if).*?-->', '', html_content, flags=re.DOTALL)
        
        return html_content.strip()
    
    @staticmethod
    def add_performance_headers(response):
        """Add performance-related headers to response."""
        # Security headers that also improve performance
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Performance headers
        response.headers['X-DNS-Prefetch-Control'] = 'on'
        
        # Compression hint
        response.headers['Vary'] = 'Accept-Encoding'
        
        return response
    
    @staticmethod
    def get_critical_resource_hints():
        """Get critical resource hints for the page head."""
        hints = []
        hints.extend(ResourceHints.get_dns_prefetch_links())
        hints.extend(ResourceHints.get_preload_links())
        
        return '\n'.join(hints)

def optimize_for_mobile():
    """Mobile-specific optimizations."""
    return {
        'viewport_meta': '<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">',
        'touch_icons': [
            '<link rel="apple-touch-icon" sizes="180x180" href="/static/icons/apple-touch-icon.png">',
            '<link rel="icon" type="image/png" sizes="32x32" href="/static/icons/favicon-32x32.png">',
            '<link rel="icon" type="image/png" sizes="16x16" href="/static/icons/favicon-16x16.png">',
        ],
        'theme_color': '<meta name="theme-color" content="#55970f">',
        'mobile_optimizations': {
            'reduce_animations': True,
            'optimize_touch_targets': True,
            'minimize_reflows': True
        }
    }