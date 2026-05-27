using UnityEngine;

namespace ParrotApp.VisualTools
{
    /// <summary>
    /// Small App-owned pixel sprites for the first formal visual-tool pass.
    /// MAG prefers the checked-in transparent reference art; runtime generation
    /// stays as a fallback for editor/test environments where Resources are absent.
    /// </summary>
    public static class VisualToolPixelSprites
    {
        private const string MagnifierResourcePath = "ParrotApp/VisualTools/MagPixelTransparent";

        private static Sprite s_shutterCircle;
        private static Sprite s_magnifier;
        private static Sprite s_whiteCircle;

        public static Sprite ShutterCircle()
        {
            if (s_shutterCircle != null) return s_shutterCircle;
            s_shutterCircle = CreateCircleSprite(
                96,
                outer: new Color(1f, 1f, 1f, 1f),
                inner: new Color(0.08f, 0.065f, 0.055f, 1f),
                ringStart: 0.68f);
            return s_shutterCircle;
        }

        public static Sprite WhiteCircle()
        {
            if (s_whiteCircle != null) return s_whiteCircle;
            s_whiteCircle = CreateCircleSprite(
                96,
                outer: new Color(1f, 1f, 1f, 1f),
                inner: new Color(1f, 1f, 1f, 0f),
                ringStart: 0.84f);
            return s_whiteCircle;
        }

        public static Sprite Magnifier()
        {
            if (s_magnifier != null) return s_magnifier;

            s_magnifier = Resources.Load<Sprite>(MagnifierResourcePath);
            if (s_magnifier != null)
                return s_magnifier;

            const int width = 112;
            const int height = 144;
            var texture = new Texture2D(width, height, TextureFormat.ARGB32, false);
            texture.wrapMode = TextureWrapMode.Clamp;
            texture.filterMode = FilterMode.Point;
            Clear(texture, width, height);

            Vector2 center = new Vector2(56f, 45f);
            DrawCircle(texture, width, height, center, 42f, new Color(0.02f, 0.025f, 0.035f, 1f));
            DrawCircle(texture, width, height, center, 36f, new Color(0.04f, 0.16f, 0.25f, 1f));
            DrawCircle(texture, width, height, center, 30f, new Color(0.76f, 0.87f, 0.94f, 0.82f));
            DrawCircle(texture, width, height, center + new Vector2(8f, -6f), 19f, new Color(0.92f, 0.97f, 1f, 0.70f));
            DrawBlock(texture, width, height, 47, 83, 18, 52, new Color(0.02f, 0.025f, 0.035f, 1f));
            DrawBlock(texture, width, height, 53, 88, 8, 42, new Color(0.07f, 0.20f, 0.30f, 1f));
            DrawBlock(texture, width, height, 58, 94, 3, 28, new Color(0.29f, 0.51f, 0.66f, 1f));
            DrawBlock(texture, width, height, 37, 80, 38, 8, new Color(0.02f, 0.025f, 0.035f, 1f));
            DrawBlock(texture, width, height, 42, 82, 28, 4, new Color(0.33f, 0.58f, 0.73f, 1f));
            DrawBlock(texture, width, height, 28, 24, 8, 18, new Color(1f, 1f, 1f, 0.95f));
            DrawBlock(texture, width, height, 42, 19, 6, 6, new Color(1f, 1f, 1f, 0.95f));

            texture.Apply();
            s_magnifier = Sprite.Create(texture, new Rect(0f, 0f, width, height), new Vector2(0.5f, 0.5f), width);
            return s_magnifier;
        }

        private static Sprite CreateCircleSprite(int size, Color outer, Color inner, float ringStart)
        {
            var texture = new Texture2D(size, size, TextureFormat.ARGB32, false);
            texture.wrapMode = TextureWrapMode.Clamp;
            texture.filterMode = FilterMode.Bilinear;
            Vector2 center = new Vector2((size - 1) * 0.5f, (size - 1) * 0.5f);
            float radius = (size - 1) * 0.5f;
            for (int y = 0; y < size; y++)
            {
                for (int x = 0; x < size; x++)
                {
                    float d = Vector2.Distance(new Vector2(x, y), center) / radius;
                    if (d > 1f)
                    {
                        texture.SetPixel(x, y, Color.clear);
                    }
                    else if (d >= ringStart)
                    {
                        float a = Mathf.SmoothStep(1f, 0f, Mathf.Clamp01((d - 0.96f) / 0.04f));
                        texture.SetPixel(x, y, new Color(outer.r, outer.g, outer.b, outer.a * a));
                    }
                    else
                    {
                        texture.SetPixel(x, y, inner);
                    }
                }
            }
            texture.Apply();
            return Sprite.Create(texture, new Rect(0f, 0f, size, size), new Vector2(0.5f, 0.5f), size);
        }

        private static void Clear(Texture2D texture, int width, int height)
        {
            for (int y = 0; y < height; y++)
            for (int x = 0; x < width; x++)
                texture.SetPixel(x, y, Color.clear);
        }

        private static void DrawCircle(Texture2D texture, int width, int height, Vector2 center, float radius, Color color)
        {
            float radiusSq = radius * radius;
            int left = Mathf.Max(0, Mathf.FloorToInt(center.x - radius));
            int right = Mathf.Min(width - 1, Mathf.CeilToInt(center.x + radius));
            int top = Mathf.Max(0, Mathf.FloorToInt(center.y - radius));
            int bottom = Mathf.Min(height - 1, Mathf.CeilToInt(center.y + radius));
            for (int y = top; y <= bottom; y++)
            for (int x = left; x <= right; x++)
            {
                Vector2 delta = new Vector2(x, y) - center;
                if (delta.sqrMagnitude <= radiusSq)
                    texture.SetPixel(x, y, color);
            }
        }

        private static void DrawBlock(Texture2D texture, int width, int height, int x, int y, int blockWidth, int blockHeight, Color color)
        {
            int left = Mathf.Clamp(x, 0, width - 1);
            int right = Mathf.Clamp(x + blockWidth, 0, width);
            int top = Mathf.Clamp(y, 0, height - 1);
            int bottom = Mathf.Clamp(y + blockHeight, 0, height);
            for (int yy = top; yy < bottom; yy++)
            for (int xx = left; xx < right; xx++)
                texture.SetPixel(xx, yy, color);
        }
    }
}
