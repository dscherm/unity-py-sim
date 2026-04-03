// Minimal System.Linq stubs for compilation gate.

namespace System.Linq
{
    public static class Enumerable
    {
        public static bool All<T>(this System.Collections.Generic.List<T> source, System.Func<T, bool> predicate) => false;
        public static bool Any<T>(this System.Collections.Generic.List<T> source, System.Func<T, bool> predicate) => false;
        public static int Count<T>(this System.Collections.Generic.List<T> source, System.Func<T, bool> predicate) => 0;
        public static System.Collections.Generic.List<T> Where<T>(this System.Collections.Generic.List<T> source, System.Func<T, bool> predicate) => null;
        public static System.Collections.Generic.List<TResult> Select<T, TResult>(this System.Collections.Generic.List<T> source, System.Func<T, TResult> selector) => null;
        public static System.Collections.Generic.List<T> ToList<T>(this System.Collections.Generic.List<T> source) => null;
        public static System.Collections.Generic.List<T> Concat<T>(this System.Collections.Generic.List<T> first, System.Collections.Generic.List<T> second) => null;
    }
}
