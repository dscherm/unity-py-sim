// Minimal System.Collections stubs for compilation gate.

namespace System
{
    public interface IDisposable
    {
        void Dispose();
    }
}

namespace System.Collections
{
    public interface IEnumerator
    {
        object Current { get; }
        bool MoveNext();
        void Reset();
    }

    public interface IEnumerable
    {
        IEnumerator GetEnumerator();
    }
}

namespace System.Collections.Generic
{
    public interface IEnumerable<T> : System.Collections.IEnumerable
    {
        new IEnumerator<T> GetEnumerator();
    }

    public interface IEnumerator<T> : System.Collections.IEnumerator, System.IDisposable
    {
        new T Current { get; }
    }

    public class List<T> : IEnumerable<T>
    {
        public int Count;
        public T this[int index] { get => default; set { } }
        public void Add(T item) { }
        public void AddRange(System.Collections.IEnumerable collection) { }
        public bool Remove(T item) => false;
        public void Insert(int index, T item) { }
        public void Clear() { }
        public bool Contains(T item) => false;
        public T[] ToArray() => default;
        public IEnumerator<T> GetEnumerator() => null;
        System.Collections.IEnumerator System.Collections.IEnumerable.GetEnumerator() => null;
    }

    public class Dictionary<TKey, TValue>
    {
        public int Count;
        public TValue this[TKey key] { get => default; set { } }
        public void Add(TKey key, TValue value) { }
        public bool ContainsKey(TKey key) => false;
        public bool TryGetValue(TKey key, out TValue value) { value = default; return false; }
    }
}
